# RAGProjectError是Exception的子类
class RAGProjectError(Exception):
    """RAG 项目的基础异常"""
    pass

# RetrievalError属于RAGProjectError也间接属于Exception
class RetrievalError(RAGProjectError):
    """检索阶段发生的异常"""
    pass

class ModelGenerationError(RAGProjectError):
    """大模型生成阶段发生的异常"""
    pass

class ConfigurationError(RAGProjectError):
    """配置或环境变量发生的异常"""
    pass

class RetryableModelError(ModelGenerationError):
    """适合重试的大模型调用异常"""
    pass

class NonRetryableModelError(ModelGenerationError):
    """不适合重试的大模型调用异常。"""
    pass
# 继承关系如下
# Exception
# └── RAGProjectError
#     ├── RetrievalError
#     ├── ModelGenerationError
#     │   ├── RetryableModelError
#     │   └── NonRetryableModelError
#     └── ConfigurationError
# 可以一次捕获所有项目异常如except RAGProjectError as error:
# 也可以只捕获一种如except RetrievalError as error:
# 比只写except Exception更清楚