/**
 * Transform text for TTS playback.
 * Keeps only Chinese characters and basic punctuation.
 * @param {string} text
 * @returns {string}
 */
export function transformTextForSpeech(text) {
  return text
    .replace(/```[\s\S]*?```/g, '')   // 移除代码块
    .replace(/`[^`]+`/g, '')          // 移除行内代码
    .replace(/\n+/g, '，')            // 换行 → 短停顿
    .replace(/[^\u4e00-\u9fff，。！？、；：…]/g, '')  // 只保留中文字符和基本标点
    .replace(/，{2,}/g, '，')         // 合并连续逗号
    .replace(/^，/, '')               // 去掉开头逗号
    .trim()
}
