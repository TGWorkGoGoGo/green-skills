---
name: mathpix-paper-translate
description: Use this skill when the user wants to translate Mathpix-exported academic markdown into polished Chinese while preserving formulas, tables, figure references, section hierarchy, and academic terminology.
---

# Mathpix Paper Translate

## 适用场景

当用户已经用 Mathpix 把英文论文 PDF 转成 Markdown，希望继续完成下列任务时，使用这个 skill：
- 将英文论文忠实精译成中文
- 保留公式、图表、表格、脚注、参考文献和章节结构
- 修正 Mathpix 导出后常见的格式错位
- 统一学术术语、变量符号和图表标题

## 输入

- 一份由 Mathpix 导出的 `.md` 文件
- 可选说明：
  - 学科领域
  - 术语偏好
  - 翻译风格
  - 只修格式或精译全文

## 工作模式

### 模式 1：`full_translate`

默认模式。适用于从英文原版 Markdown 直接得到中文精译稿。
目标：
- 全文翻译为中文
- 保留原有标题层级
- 保留公式块、行内公式、编号、变量名
- 保留图题、表题、注释、附录结构
- 对导出错位的列表、段落、空行、公式块、图表占位进行修正
- 对明显生硬的直译做学术化润色

### 模式 2：`format_only`

适用于译文已经存在，只需要修格式、清结构、统一表达的情况。
目标：
- 不改动核心语义
- 修正标题层级、段落断裂、列表缩进、公式前后空行
- 统一图题、表题、脚注、术语写法
- 清理多余空格、重复换行、明显的 OCR 痕迹

## 核心规则

1. 公式优先保真。不要改变量符号、上下标、编号和推导结构。
2. 图表优先保真。图题、表题、图注、表注应尽量对应原文位置。
3. 学术术语优先一致。全文同一术语尽量只保留一种主译法。
4. 结构优先清晰。标题层级、段落关系、列表关系要稳定。
5. 译文优先可读。中文表达要符合学术写作习惯，避免机械硬译。

## 推荐工作流

### 第一步：读取 Mathpix 导出的 Markdown

先快速检查下列内容：
- 标题层级是否完整
- 公式是否以代码块或行内公式保留
- 图表标题是否仍在
- 参考文献区是否完整
- 是否存在明显错位或断裂

### 第二步：确定模式

如果输入仍是英文原版 Markdown，使用 `full_translate`。
如果输入已经有中文译稿，只需要修排版和统一术语，使用 `format_only`。

### 第三步：执行翻译或修订

处理时应显式关注：
- 章节标题
- 摘要与关键词
- 行内公式与展示公式
- 图题、表题、图注、表注
- 变量定义
- 脚注与参考文献

### 第四步：输出版本化结果

建议：
- 不覆盖原稿
- 输出到 `output/`
- 文件名使用 `{原文件名} - v#`
- 同时输出 `{原文件名} - v# - changes.md`

`changes.md` 至少记录：
- 修订模式
- 调整的段落数量
- 修正的公式、图表、表格数量
- 统一过的关键术语
- 仍需人工复核的地方

## 建议提示词

### 默认调用

```text
请使用 mathpix-paper-translate skill 处理这份由 Mathpix 导出的论文 Markdown。
模式：full_translate
要求：保留公式、图表、表格、脚注、参考文献和标题层级；修正格式问题；输出中文精译稿，并附 changes.md。
```

### 只修格式

```text
请使用 mathpix-paper-translate skill 处理这份 Markdown。
模式：format_only
要求：不改核心语义，重点修正标题层级、段落断裂、公式块、图表标题和术语一致性，并附 changes.md。
```

## 完成标准

- 中文译文可连续阅读
- 公式与变量未被破坏
- 图表标题和正文对应关系清楚
- 标题层级稳定
- changes.md 能说明本轮加工做了什么
