# LangChain RAG 评估报告

配套文件：rag\_embedding\_langchain\_test.xlsx / rag\_langchain\_knowledge\_word.docx

## 1. 评估目标

本报告用于验证 LangChain RAG 流程中检索结果是否能够稳定命中预期知识块，并给出基础的生成质量检查框架。

## 2. 测试集概览

当前测试集包含 8 条查询、10 条知识记录。每条查询都绑定一个 Expected Knowledge ID，并以 Hit@1 为默认通过标准。

<table><tr><td rowspan=1 colspan=1>ID</td><td rowspan=1 colspan=1>测试问题</td><td rowspan=1 colspan=1>预期知识</td><td rowspan=1 colspan=1>标准</td></tr><tr><td rowspan=1 colspan=1>T001</td><td rowspan=1 colspan=1>LangChain 里常用什么方法做递归文本切分？</td><td rowspan=1 colspan=1>K002</td><td rowspan=1 colspan=1>Hit@1</td></tr><tr><td rowspan=1 colspan=1>T002</td><td rowspan=1 colspan=1>FAISS 和 Chroma 在RAG 中主要负责什么？</td><td rowspan=1 colspan=1>K004</td><td rowspan=1 colspan=1>Hit@1</td></tr><tr><td rowspan=1 colspan=1>T003</td><td rowspan=1 colspan=1>怎么减少召回结果内容过于相似？</td><td rowspan=1 colspan=1>K006</td><td rowspan=1 colspan=1>Hit@1</td></tr><tr><td rowspan=1 colspan=1>T004</td><td rowspan=1 colspan=1>RAG 的检索效果常用哪些指标评估？</td><td rowspan=1 colspan=1>K008</td><td rowspan=1 colspan=1>Hit@1</td></tr><tr><td rowspan=1 colspan=1>T005</td><td rowspan=1 colspan=1>为什么知识块要保存source 和 version ?</td><td rowspan=1 colspan=1>K009</td><td rowspan=1 colspan=1>Hit@1</td></tr><tr><td rowspan=1 colspan=1>T006</td><td rowspan=1 colspan=1>RAG 提示词怎样降低幻觉？</td><td rowspan=1 colspan=1>K007</td><td rowspan=1 colspan=1>Hit@1</td></tr><tr><td rowspan=1 colspan=1>T007</td><td rowspan=1 colspan=1>Embedding 在 RAG 中起什么作用？</td><td rowspan=1 colspan=1>K003</td><td rowspan=1 colspan=1>Hit@1</td></tr><tr><td rowspan=1 colspan=1>T008</td><td rowspan=1 colspan=1>top-k 太大可能有什么问题？</td><td rowspan=1 colspan=1>K010</td><td rowspan=1 colspan=1>Hit@1</td></tr></table>

## 3. 建议评估指标

检索层：Hit@K / Recall@K / MRR；生成层：答案相关性、忠实度、上下文相关性。对于小型测试集，可先以Expected Knowledge ID 是否进入 Top-K 作为最直接的回归指标。

## 4. 执行建议

将 Excel 中的 Query 逐条送入 Retriever，记录预期知识块的 Actual Rank。Excel 的 Pass 列会依据Expected Hit@K 自动判断。若检索通过但最终答案不稳定，再检查 Prompt、上下文拼接与模型生成参数。

## 5. 常见调优方向

优先检查 chunk\_size / chunk\_overlap、Embedding 模型、top-k、MMR、元数据过滤和重排序。每次只修改一个关键变量并重新跑同一批测试，便于确认改动是否真正提升检索效果。