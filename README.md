# RAG Knowledge Base Assistant

一个基于 LangChain、Hugging Face Embedding 和 Chroma 的本地知识库问答系统。

## 当前功能

- 支持 TXT、Markdown、PDF、Word、CSV 和 Excel
- 文档切分与向量化
- Chroma 本地向量数据库
- 相似度检索与距离阈值过滤
- 基于资料生成回答
- 显示参考来源和文本块编号
- 启动健康检查
- 日志记录
- 统一返回结果结构
- 检索、生成和总耗时统计
- 模型调用失败重试与降级处理

## 项目结构

```text
rag_project/
├── docs/
├── build_vector_db.py
├── chains.py
├── config.py
├── exceptions.py
├── health_check.py
├── loaders.py
├── logger.py
├── prompts.py
├── rag_qa.py
├── schemas.py
└── vector_db.py

安装依赖
pip install -r requirements.txt

配置环境变量
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://your-api-base-url/v1
OPENAI_MODEL=your_model_name

构建向量数据库
python build_vector_db.py

启动问答系统
python rag_qa.py