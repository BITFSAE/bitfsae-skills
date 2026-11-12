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

Choose the tone for the document's role and audience before writing:

| Document role | Typical examples | Tone |
| --- | --- | --- |
| Repository contracts and specs | `README.md`, interface specs, config tables, `CHANGELOG.md`, code comments | Most restrained and exact: what it is, what it does, under which condition |
| Design calculations and scrutineering docs | ESF/SES sheets, thermal or structural checks, review defenses | Objective and rigorous: state boundary conditions, safety margins, and conclusions up front |
| Internal learning, notes, and reviews | Technical notes, principle summaries, design comparisons, postmortems, troubleshooting, handover | Plain and readable: prioritize key findings and cause-effect; use concrete comparisons, scale checks, and clear engineering judgments |

- For a long or multi-part section, summarize first and expand afterwards; let headings and opening sentences carry the key status or conclusion.
- State the reason and the benefit where the reader needs them to decide or to avoid undoing a design choice.
- Leave out slogans, lectures, filler, and repetition.

## 2. Wording to avoid

- Commercial and internet wording: 赋能, 打造, 一站式, 极致, 无缝, 强大, 丝滑, 闭环, 抓手, and similar. Name the concrete function instead.
- Exaggeration, emotional or attacking wording, and empty self-assessment such as "设计优秀", "非常稳定", "致命", "硬伤", or "站不住脚". Replace them with measured values, conditions, or supported engineering judgments such as "明显错误", "相互抵消", or "可以忽略" backed immediately by numbers.
- Absolute words: 最, 完全, 绝对, 100%, 一定, 永远, 彻底. Give the actual range, condition, or count. Defined quantities, parameter names (such as "最大充电电流" or "100% 占空比"), and judgments with explicit quantitative bounds (such as "占比 1.4%，可以忽略") stay.

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
- When explaining an error or mismatch, state the counterintuitive scale or physical consequence directly (for example, "对应宽度需 223 mm，不符合箱体尺寸") instead of stiff, roundabout phrasing.

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
- Does the tone match the document's role, and can a reader grasp the core conclusion, severity, and cause-effect in one pass without key points being softened into ambiguity?
- Is anything needed to understand the implementation missing?
