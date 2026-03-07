"""
OCR Recognition Module

Uses EasyOCR to recognise text within cropped image regions.
Supports Simplified Chinese + English (matching hospital signage).

Typical usage:
    1. BlackBoxSegmenter detects sign bounding boxes
    2. Caller crops each region from the original image
    3. OCRRecognizer.recognize(cropped_bgr) reads the text
"""

import asyncio
import base64
import time
from typing import List, Optional, Tuple

import cv2
import numpy as np
from pydantic import BaseModel
import easyocr


# ── Pydantic result model ──────────────────────────────────────────────────────

class OCRResult(BaseModel):
    """Result of OCR recognition."""

    success: bool
    detected_text: Optional[str] = None       # All detected text joined by space
    confidence: Optional[float] = None        # Average confidence across all detections
    bounding_boxes: List[Tuple[int, int, int, int]] = []  # (x1,y1,x2,y2) per detection
    languages: List[str] = []
    error_message: Optional[str] = None
    processing_time_ms: Optional[float] = None


# ── Helper ─────────────────────────────────────────────────────────────────────

def _quad_to_xyxy(quad: list) -> Tuple[int, int, int, int]:
    """
    Convert EasyOCR 4-corner quad [[x,y], ...] → (x1, y1, x2, y2).

    EasyOCR returns corners as [[TL], [TR], [BR], [BL]].
    """
    xs = [int(p[0]) for p in quad]
    ys = [int(p[1]) for p in quad]
    return min(xs), min(ys), max(xs), max(ys)


# ── Main class ─────────────────────────────────────────────────────────────────

class OCRRecognizer:
    """
    Recognises text in image crops using EasyOCR.

    - EasyOCR Reader is loaded lazily on first call (heavy, ~300 MB).
    - All inference runs in a thread-pool executor so asyncio is never blocked.
    - Languages: Simplified Chinese ('ch_sim') + English ('en').
    """

    LANGUAGES = ['ch_sim', 'en']

    def __init__(self) -> None:
        self._reader: Optional[easyocr.Reader] = None

    # ── Internal ──────────────────────────────────────────────────────────────

    def _ensure_reader(self) -> None:
        """Lazily initialise the EasyOCR reader."""
        if self._reader is not None:
            return
        print(f"[OCRRecognizer] Loading EasyOCR (languages: {self.LANGUAGES}) ...")
        self._reader = easyocr.Reader(self.LANGUAGES, gpu=False)
        print("[OCRRecognizer] EasyOCR ready.")

    def _run_ocr(self, image_rgb: np.ndarray) -> list:
        """
        Synchronous EasyOCR call (runs in thread-pool executor).

        Returns raw EasyOCR result list: [[bbox, text, conf], ...]
        """
        assert self._reader is not None
        return self._reader.readtext(image_rgb)

    # ── Public API ────────────────────────────────────────────────────────────

    async def recognize(self, image_data: np.ndarray) -> OCRResult:
        """
        Recognise text in a BGR numpy image (e.g. a cropped sign region).

        Args:
            image_data: BGR image array (H, W, 3), as returned by cv2.imread
                        or a crop from the segmenter bounding boxes.

        Returns:
            OCRResult with all detected text joined and per-word bounding boxes.
        """
        t0 = time.perf_counter()
        try:
            self._ensure_reader()

            # EasyOCR works on RGB
            image_rgb = cv2.cvtColor(image_data, cv2.COLOR_BGR2RGB)

            loop    = asyncio.get_running_loop()
            results = await loop.run_in_executor(None, self._run_ocr, image_rgb)

            if not results:
                return OCRResult(
                    success=True,
                    detected_text="",
                    confidence=0.0,
                    languages=self.LANGUAGES,
                    processing_time_ms=(time.perf_counter() - t0) * 1000,
                )

            texts      = []
            confs      = []
            boxes: List[Tuple[int, int, int, int]] = []

            for (bbox, text, conf) in results:
                texts.append(text.strip())
                confs.append(float(conf))
                boxes.append(_quad_to_xyxy(bbox))

            return OCRResult(
                success=True,
                detected_text=" ".join(texts),
                confidence=sum(confs) / len(confs),
                bounding_boxes=boxes,
                languages=self.LANGUAGES,
                processing_time_ms=(time.perf_counter() - t0) * 1000,
            )

        except Exception as exc:
            return OCRResult(
                success=False,
                error_message=f"OCR recognition error: {exc}",
                processing_time_ms=(time.perf_counter() - t0) * 1000,
            )

    async def recognize_base64(self, image_base64: str) -> OCRResult:
        """
        Recognise text from a base64-encoded JPEG/PNG image.

        Args:
            image_base64: Base64-encoded image string.

        Returns:
            OCRResult with all detected text joined and per-word bounding boxes.
        """
        t0 = time.perf_counter()
        try:
            img_bytes = base64.b64decode(image_base64)
            nparr     = np.frombuffer(img_bytes, np.uint8)
            image_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if image_bgr is None:
                return OCRResult(
                    success=False,
                    error_message="Failed to decode base64 image — unsupported format or corrupt data",
                    processing_time_ms=(time.perf_counter() - t0) * 1000,
                )

            result = await self.recognize(image_bgr)
            result.processing_time_ms = (time.perf_counter() - t0) * 1000
            return result

        except Exception as exc:
            return OCRResult(
                success=False,
                error_message=f"Base64 OCR error: {exc}",
                processing_time_ms=(time.perf_counter() - t0) * 1000,
            )


# ── Module-level singleton ─────────────────────────────────────────────────────

_ocr_instance: Optional[OCRRecognizer] = None


def get_ocr_recognizer() -> OCRRecognizer:
    """Return the global OCRRecognizer singleton, creating it if necessary."""
    global _ocr_instance
    if _ocr_instance is None:
        _ocr_instance = OCRRecognizer()
    return _ocr_instance


async def recognize_text(image_data: np.ndarray) -> OCRResult:
    """
    Convenience coroutine: recognise text in a BGR numpy image.

    Args:
        image_data: BGR image (numpy array)

    Returns:
        OCRResult
    """
    return await get_ocr_recognizer().recognize(image_data)


__all__ = [
    "OCRResult",
    "OCRRecognizer",
    "get_ocr_recognizer",
    "recognize_text",
]
