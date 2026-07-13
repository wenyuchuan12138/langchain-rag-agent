# 放统一配置，比如路径、模型名等

DOCS_DIR = "docs"
CHROMA_DIR = "chroma_db"
LOGS_DIR = "logs"
LOG_FILE = "logs/rag_project.log"

EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

CHUNK_SIZE = 100
CHUNK_OVERLAP = 20

TOP_K = 3
MAX_DISTANCE = 2.0

SUPPORTED_EXTENSIONS = [".txt", ".md", ".pdf", ".docx", ".csv", ".xlsx"]

# 大模型调用超时时间以秒为单位
LLM_TIMEOUT = 30
# 最多尝试次数，包括第一次调用
MAX_RETRIES = 3
# 第一次重试前等待时间
RETRY_BASE_DELAY = 1.0

INCOMING_DIR = "incoming"
PROCESSED_DIR = "processed"
FAILED_DIR = "failed"

MANIFEST_FILE = "index_manifest.json"