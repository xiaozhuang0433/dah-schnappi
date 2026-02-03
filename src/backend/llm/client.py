"""
LLM Client Factory

根据配置创建对应的 LLM 客户端实例。
"""
from typing import Optional
from .base import LLMClientABC
from .claude import ClaudeClient
from .openai import OpenAIClient
from ..config.settings import settings
from ..utils.logger import get_logger


logger = get_logger(__name__)


class LLMClientFactory:
    """LLM 客户端工厂

    根据配置创建对应的 LLM 客户端实例。
    """

    @staticmethod
    def create_client(
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        **kwargs
    ) -> LLMClientABC:
        """创建 LLM 客户端实例

        Args:
            provider: LLM 提供商（claude, openai），如果为 None 则使用配置中的默认值
            api_key: API 密钥，如果为 None 则从配置中读取
            **kwargs: 其他配置参数

        Returns:
            LLM 客户端实例

        Raises:
            ValueError: 如果提供商不支持或 API 密钥未配置
        """
        if provider is None:
            provider = settings.LLM_PROVIDER

        # 确定使用的 API 密钥
        if api_key is None:
            if provider == "claude":
                api_key = settings.ANTHROPIC_API_KEY
            elif provider == "openai":
                api_key = settings.OPENAI_API_KEY
            else:
                raise ValueError(f"Unsupported LLM provider: {provider}")

        if not api_key:
            raise ValueError(f"API key is required for {provider}. Please set the corresponding environment variable.")

        # 根据提供商创建对应的客户端
        if provider == "claude":
            return LLMClientFactory._create_claude_client(api_key, **kwargs)
        elif provider == "openai":
            return LLMClientFactory._create_openai_client(api_key, **kwargs)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    @staticmethod
    def _create_claude_client(api_key: str, **kwargs) -> ClaudeClient:
        """创建 Claude 客户端"""
        model = kwargs.get("model", settings.LLM_MODEL)
        temperature = kwargs.get("temperature", settings.LLM_TEMPERATURE)
        max_tokens = kwargs.get("max_tokens", settings.LLM_MAX_TOKENS)

        logger.info(f"Creating Claude client with model: {model}")
        return ClaudeClient(
            api_key=api_key,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )

    @staticmethod
    def _create_openai_client(api_key: str, **kwargs) -> OpenAIClient:
        """创建 OpenAI 客户端"""
        model = kwargs.get("model", settings.LLM_MODEL)
        temperature = kwargs.get("temperature", settings.LLM_TEMPERATURE)
        max_tokens = kwargs.get("max_tokens", settings.LLM_MAX_TOKENS)
        base_url = kwargs.get("base_url", settings.OPENAI_BASE_URL)

        logger.info(f"Creating OpenAI client with model: {model}")
        return OpenAIClient(
            api_key=api_key,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            base_url=base_url
        )

    @staticmethod
    def get_default_client() -> LLMClientABC:
        """获取默认的 LLM 客户端

        Returns:
            默认配置的 LLM 客户端实例

        Raises:
            ValueError: 如果配置不完整
        """
        return LLMClientFactory.create_client()


def get_llm_client() -> LLMClientABC:
    """获取全局 LLM 客户端实例（便捷函数）"""
    return LLMClientFactory.get_default_client()
