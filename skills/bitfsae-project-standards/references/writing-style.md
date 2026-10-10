# Writing Style

Applies to documents, code comments, changelog entries, and reports. BITFSAE documents are written in Chinese, so the wording examples below are Chinese.

## Contents

1. Tone
2. Wording to avoid
3. Positive statements and negation
4. Plain language
5. Order and structure
6. Completeness
7. Revision checklist

## 1. Tone

- Use plain, direct engineering sentences: what it is, what it does, under which condition.
- For a long or multi-part section, summarize first and expand afterwards.
- State the reason and the benefit where the reader needs them to decide or to avoid undoing a design choice.
- Leave out slogans, lectures, filler, and repetition.

## 2. Wording to avoid

- Commercial and internet wording: 赋能, 打造, 一站式, 极致, 无缝, 强大, 丝滑, 闭环, 抓手, and similar. Name the concrete function instead.
- Exaggeration, emotional wording, and self-assessment such as "设计优秀" or "非常稳定". Give a measured value, a test result, or the condition.
- Absolute words: 最, 完全, 绝对, 100%, 一定, 永远, 彻底. Give the actual range, condition, or count. Defined quantities and parameter names such as "最大充电电流" or "100% 占空比" are values and stay.

## 3. Positive statements and negation

- State rules and conclusions positively. Say what it is and what it is for, then give the decision rule.
- Express completion conditions as observable signals, for example "以保存等待位清零为准" or "看 X 字段".
- Use "不是……而是……" sparingly and keep negative sentences few. A short negation that reads clearly in one pass stays.
- Add a clarification only where readers are likely to misunderstand, and give its reason or mechanism. Delete negations that have no reason, such as "不代表 X" and "不能只看 X".
- When a section says how to handle something, also say why.

Example:

- Before: 「保存是否完成，不是看命令应答，而是看保存等待位。」
- After: 「以保存等待位清零为准。命令应答只表示命令已收到，此时数据可能仍在写入。」

## 4. Plain language

- A heading states what the section contains.
- Use common words and short sentences. Replace abstract wording such as 门控, 语义, 消费, 落盘, 原子, 临界区 with the action itself, for example 写入 Flash or 读取.
- When a protocol or standard requires a term, explain it in plain words at its first appearance.

## 5. Order and structure

- Order a document as: responsibility → implemented flow → interface or protocol → exceptions → debugging and verification.
- Keep implemented behavior apart from pending work. Put calibration, integration tests, unconfirmed parameters, and known gaps at the end or in an appendix.
- Place rare-fault handling after the main flow. State the trigger condition, the action, the reason, and which flows stay unaffected.
- State each conclusion in full once. Elsewhere, refer to it briefly.

## 6. Completeness

The goal is that a reader understands the whole implementation from the document alone. Correctness and completeness come before brevity. When shortening, keep what is needed to understand the code, interfaces, parameters, action conditions, processing order, the reason for each setting, and the verification method.

## 7. Revision checklist

Judge each item by whether a reader grasps the text in one pass. Do not apply them mechanically.

- Is each rule stated positively where that reads more clearly?
- Does each completion condition name an observable signal?
- Does any negation lack a reason?
- Is any conclusion stated in full more than once?
- Does any text contain marketing wording, self-assessment, or an absolute word that is not a defined quantity?
- Is anything needed to understand the implementation missing?
