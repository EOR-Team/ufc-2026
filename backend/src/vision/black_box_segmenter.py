"""
Black Box Segmentation Module

Uses YOLOv5s ONNX model (85-col detection output) to detect black box
regions (text label signs) in images for visual destination verification.

Input size : 640×640 (letterbox padded, aspect ratio preserved)
Model path : configured via config.general.BLACK_BOX_SEGMENTATION_MODEL_PATH
             → backend/src/model/yolov5s.onnx
"""

import asyncio
import base64
import time
from typing import List, Optional, Tuple

import cv2
import numpy as np
import onnxruntime as ort
from pydantic import BaseModel, Field

from src.config.general import BLACK_BOX_SEGMENTATION_MODEL_PATH


# ── Pydantic result model ──────────────────────────────────────────────────────

class SegmentationResult(BaseModel):
    """Result of black box segmentation."""

    success: bool = Field(..., description="Segmentation process success")
    bounding_boxes: List[Tuple[int, int, int, int]] = Field(
        default_factory=list,
        description="Detected bounding boxes as (x1, y1, x2, y2) in original image coords",
    )
    confidence_scores: List[float] = Field(
        default_factory=list,
        description="Confidence scores corresponding to each bounding box",
    )
    error_message: Optional[str] = None
    processing_time_ms: Optional[float] = None



# ── Preprocessing helpers ──────────────────────────────────────────────────────

def _letterbox(
    image: np.ndarray,
    target_size: int = 640,
    pad_color: Tuple[int, int, int] = (114, 114, 114),
) -> Tuple[np.ndarray, float, Tuple[int, int]]:
    """
    Resize image with letterbox padding to keep aspect ratio.

    Returns:
        padded    : Padded & resized image (target_size × target_size, RGB)
        scale     : Uniform scale factor applied to the original
        pad       : (pad_left, pad_top) in pixels
    """
    h, w = image.shape[:2]
    scale = min(target_size / h, target_size / w)
    new_w = int(round(w * scale))
    new_h = int(round(h * scale))

    resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

    pad_w  = (target_size - new_w) / 2
    pad_h  = (target_size - new_h) / 2
    top    = int(round(pad_h - 0.1))
    bottom = int(round(pad_h + 0.1))
    left   = int(round(pad_w - 0.1))
    right  = int(round(pad_w + 0.1))

    padded = cv2.copyMakeBorder(
        resized, top, bottom, left, right,
        cv2.BORDER_CONSTANT, value=pad_color,
    )
    return padded, scale, (left, top)


def _preprocess(image_bgr: np.ndarray, input_size: int = 640) -> np.ndarray:
    """
    Convert a BGR OpenCV image to a model input tensor.

    Returns:
        float32 NCHW tensor with shape (1, 3, input_size, input_size), values in [0, 1]
    """
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    padded, _, _ = _letterbox(image_rgb, target_size=input_size)
    tensor = padded.astype(np.float32) / 255.0
    tensor = np.transpose(tensor, (2, 0, 1))   # HWC → CHW
    tensor = np.expand_dims(tensor, axis=0)    # CHW → NCHW
    return np.ascontiguousarray(tensor)


# ── Postprocessing helpers ─────────────────────────────────────────────────────

def _xywh2xyxy(boxes: np.ndarray) -> np.ndarray:
    """Convert centre-format [cx, cy, w, h] → corner-format [x1, y1, x2, y2]."""
    out = np.empty_like(boxes)
    out[:, 0] = boxes[:, 0] - boxes[:, 2] / 2  # x1
    out[:, 1] = boxes[:, 1] - boxes[:, 3] / 2  # y1
    out[:, 2] = boxes[:, 0] + boxes[:, 2] / 2  # x2
    out[:, 3] = boxes[:, 1] + boxes[:, 3] / 2  # y2
    return out


def _nms(
    boxes_xyxy: np.ndarray,
    scores: np.ndarray,
    iou_threshold: float = 0.45,
) -> List[int]:
    """
    Non-Maximum Suppression via OpenCV.

    Args:
        boxes_xyxy   : (N, 4) array of [x1, y1, x2, y2]
        scores       : (N,)   confidence scores
        iou_threshold: IoU overlap threshold

    Returns:
        List of kept indices.
    """
    # cv2.dnn.NMSBoxes expects [x, y, w, h]
    boxes_xywh = boxes_xyxy.copy()
    boxes_xywh[:, 2] = boxes_xyxy[:, 2] - boxes_xyxy[:, 0]  # w
    boxes_xywh[:, 3] = boxes_xyxy[:, 3] - boxes_xyxy[:, 1]  # h

    indices = cv2.dnn.NMSBoxes(
        bboxes=boxes_xywh.tolist(),
        scores=scores.tolist(),
        score_threshold=0.0,         # already pre-filtered
        nms_threshold=iou_threshold,
    )
    if isinstance(indices, np.ndarray):
        return indices.flatten().tolist()
    return []


def _postprocess(
    raw_output: np.ndarray,
    orig_shape: Tuple[int, int],
    input_size: int = 640,
    conf_threshold: float = 0.25,
    iou_threshold: float = 0.45,
) -> Tuple[List[Tuple[int, int, int, int]], List[float]]:
    """
    Parse YOLOv5s (detection) output[0] tensor into bounding boxes.

    YOLOv5s output[0] shape: (1, num_anchors, 85)
        cols  0-3  : cx, cy, w, h  (in input_size coordinate space)
        col   4    : objectness score
        cols  5-84 : class scores  (80 COCO classes)

    For our custom-trained single-class model (black_box), only class 0
    matters — but we keep all classes here so the same code works with
    both COCO pretrained and fine-tuned weights.

    Args:
        raw_output    : outputs[0] from ONNX session, shape (1, N, 85)
        orig_shape    : (H, W) of the original image before preprocessing
        input_size    : model input side length (640)
        conf_threshold: minimum confidence to keep a detection
        iou_threshold : NMS IoU threshold

    Returns:
        bboxes : list of (x1, y1, x2, y2) in original-image pixel coordinates
        scores : corresponding confidence values
    """
    preds = raw_output[0]                                    # (N, 85)

    objectness   = preds[:, 4]                               # (N,)
    class_scores = preds[:, 5:85]                            # (N, 80)
    confidence   = objectness * class_scores.max(axis=1)    # (N,)

    keep_mask = confidence > conf_threshold
    if not keep_mask.any():
        return [], []

    filtered_preds = preds[keep_mask]
    filtered_conf  = confidence[keep_mask]

    boxes_xyxy   = _xywh2xyxy(filtered_preds[:, :4])
    kept_indices = _nms(boxes_xyxy, filtered_conf, iou_threshold)
    if not kept_indices:
        return [], []

    boxes_xyxy  = boxes_xyxy[kept_indices]
    scores_kept = filtered_conf[kept_indices]

    # Rescale from input_size space back to original image space
    orig_h, orig_w = orig_shape
    scale_x = orig_w / input_size
    scale_y = orig_h / input_size

    result_boxes:  List[Tuple[int, int, int, int]] = []
    result_scores: List[float] = []

    for box, score in zip(boxes_xyxy, scores_kept):
        x1 = max(0, int(box[0] * scale_x))
        y1 = max(0, int(box[1] * scale_y))
        x2 = min(orig_w, int(box[2] * scale_x))
        y2 = min(orig_h, int(box[3] * scale_y))
        result_boxes.append((x1, y1, x2, y2))
        result_scores.append(float(score))

    return result_boxes, result_scores


# ── Main class ─────────────────────────────────────────────────────────────────

class BlackBoxSegmenter:
    """
    Detects black box regions (text label signs) using YOLOv5-seg ONNX inference.

    - ONNX session is loaded lazily on first call and cached for reuse.
    - Inference runs in a thread-pool executor so it never blocks the asyncio loop.
    - Input size: 640×640 (letterbox padded, aspect ratio preserved).
    """

    INPUT_SIZE     = 640
    CONF_THRESHOLD = 0.25
    IOU_THRESHOLD  = 0.45

    def __init__(self, model_path: Optional[str] = None) -> None:
        """
        Args:
            model_path: Absolute path to the YOLOv5-seg ONNX file.
                        Defaults to config.BLACK_BOX_SEGMENTATION_MODEL_PATH.
        """
        self._model_path  = model_path or str(BLACK_BOX_SEGMENTATION_MODEL_PATH)
        self._session:    Optional[ort.InferenceSession] = None
        self._input_name: Optional[str] = None

    def _ensure_session(self) -> None:
        """Lazily initialise the ONNX Runtime inference session."""
        if self._session is not None:
            return
        print(f"[BlackBoxSegmenter] Loading ONNX model: {self._model_path}")
        session = ort.InferenceSession(
            self._model_path,
            providers=["CPUExecutionProvider"],
        )
        self._input_name = session.get_inputs()[0].name
        self._session = session
        print("[BlackBoxSegmenter] Model loaded successfully.")

    def _run_inference(self, tensor: np.ndarray) -> List[np.ndarray]:
        """Synchronous ONNX inference (called from thread-pool executor)."""
        assert self._session is not None, "ONNX session not initialised"
        assert self._input_name is not None, "ONNX input name not initialised"
        return self._session.run(None, {self._input_name: tensor})

    async def segment(self, image_data: np.ndarray) -> SegmentationResult:
        """
        Detect black box sign regions from a BGR numpy image.

        Args:
            image_data: BGR image array (H, W, 3), as returned by cv2.imread.

        Returns:
            SegmentationResult containing bounding boxes and confidence scores.
        """
        t0 = time.perf_counter()
        try:
            self._ensure_session()

            orig_shape = image_data.shape[:2]                    # (H, W)
            tensor     = _preprocess(image_data, self.INPUT_SIZE)

            # Offload blocking ONNX inference to thread pool
            loop    = asyncio.get_running_loop()
            outputs = await loop.run_in_executor(None, self._run_inference, tensor)

            boxes, scores = _postprocess(
                outputs[0],
                orig_shape,
                self.INPUT_SIZE,
                self.CONF_THRESHOLD,
                self.IOU_THRESHOLD,
            )

            return SegmentationResult(
                success=True,
                bounding_boxes=boxes,
                confidence_scores=scores,
                processing_time_ms=(time.perf_counter() - t0) * 1000,
            )

        except Exception as exc:
            return SegmentationResult(
                success=False,
                error_message=f"Segmentation error: {exc}",
                processing_time_ms=(time.perf_counter() - t0) * 1000,
            )

    async def segment_base64(self, image_base64: str) -> SegmentationResult:
        """
        Detect black box sign regions from a base64-encoded JPEG/PNG image.

        Args:
            image_base64: Base64-encoded image string.

        Returns:
            SegmentationResult containing bounding boxes and confidence scores.
        """
        t0 = time.perf_counter()
        try:
            img_bytes = base64.b64decode(image_base64)
            nparr     = np.frombuffer(img_bytes, np.uint8)
            image_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if image_bgr is None:
                return SegmentationResult(
                    success=False,
                    error_message="Failed to decode base64 image — unsupported format or corrupt data",
                    processing_time_ms=(time.perf_counter() - t0) * 1000,
                )

            result = await self.segment(image_bgr)
            # Override timing to cover the full base64 → result path
            result.processing_time_ms = (time.perf_counter() - t0) * 1000
            return result

        except Exception as exc:
            return SegmentationResult(
                success=False,
                error_message=f"Base64 segmentation error: {exc}",
                processing_time_ms=(time.perf_counter() - t0) * 1000,
            )


# ── Module-level singleton ─────────────────────────────────────────────────────

_segmenter_instance: Optional[BlackBoxSegmenter] = None


def get_black_box_segmenter(model_path: Optional[str] = None) -> BlackBoxSegmenter:
    """
    Return the global BlackBoxSegmenter singleton, creating it if necessary.

    Args:
        model_path: Optional custom ONNX model path (only used on first call).
    """
    global _segmenter_instance
    if _segmenter_instance is None:
        _segmenter_instance = BlackBoxSegmenter(model_path=model_path)
    return _segmenter_instance


async def segment_black_boxes(
    image_data: np.ndarray,
    model_path: Optional[str] = None,
) -> SegmentationResult:
    """
    Convenience coroutine: detect black boxes in a BGR numpy image.

    Args:
        image_data : BGR image (numpy array)
        model_path : Optional custom model path

    Returns:
        SegmentationResult
    """
    return await get_black_box_segmenter(model_path).segment(image_data)


__all__ = [
    "SegmentationResult",
    "BlackBoxSegmenter",
    "get_black_box_segmenter",
    "segment_black_boxes",
]
