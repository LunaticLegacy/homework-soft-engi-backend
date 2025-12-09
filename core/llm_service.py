from modules.llm_fetcher import LLMFetcher
from core.config import load_config

config = load_config()
llm_config = config.get("llm", {})

def get_llm_fetcher() -> LLMFetcher:
    """
    获取LLM获取器实例的依赖注入函数
    
    Returns:
        LLMFetcher: LLM获取器实例
    """
    # 从配置中获取API密钥等信息
    config = load_config()
    llm_config = config.get("llm", {})
    
    return LLMFetcher(**llm_config)