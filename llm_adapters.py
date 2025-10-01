# llm_adapters.py
# -*- coding: utf-8 -*-
import logging
import time
from typing import Optional
from langchain_openai import ChatOpenAI, AzureChatOpenAI
# from google import genai
import google.generativeai as genai
# from google.genai import types
from google.generativeai import types
from openai import OpenAI
import requests

# 可选依赖 - 延迟导入
def _import_azure_components():
    """延迟导入Azure组件"""
    try:
        from azure.ai.inference import ChatCompletionsClient
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.inference.models import SystemMessage, UserMessage
        return ChatCompletionsClient, AzureKeyCredential, SystemMessage, UserMessage
    except ImportError:
        return None, None, None, None


def check_base_url(url: str) -> str:
    """
    处理base_url的规则：
    1. 如果url以#结尾，则移除#并直接使用用户提供的url
    2. 否则检查是否需要添加/v1后缀
    """
    import re
    url = url.strip()
    if not url:
        return url
        
    if url.endswith('#'):
        return url.rstrip('#')
        
    if not re.search(r'/v\d+$', url):
        if '/v1' not in url:
            url = url.rstrip('/') + '/v1'
    return url

class BaseLLMAdapter:
    """
    统一的 LLM 接口基类，为不同后端（OpenAI、Ollama、ML Studio、Gemini等）提供一致的方法签名。
    """
    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def invoke(self, prompt: str) -> str:
        raise NotImplementedError("Subclasses must implement .invoke(prompt) method.")

    def _invoke_with_retry(self, invoke_func, prompt: str, *args, **kwargs) -> str:
        """带重试机制的调用方法"""
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                return invoke_func(prompt, *args, **kwargs)
            except Exception as e:
                last_exception = e

                if attempt < self.max_retries:
                    # 判断是否为可重试的错误
                    if self._is_retryable_error(e):
                        wait_time = self.retry_delay * (2 ** attempt)  # 指数退避
                        logging.warning(f"API调用失败，{wait_time}秒后重试 (尝试 {attempt + 1}/{self.max_retries + 1}): {e}")
                        time.sleep(wait_time)
                        continue
                    else:
                        # 不可重试的错误，直接返回
                        logging.error(f"API调用遇到不可重试错误: {e}")
                        return ""
                else:
                    logging.error(f"API调用失败，已达到最大重试次数: {e}")

        return ""

    def _is_retryable_error(self, error: Exception) -> bool:
        """判断错误是否可重试"""
        error_str = str(error).lower()

        # 网络相关错误
        if any(keyword in error_str for keyword in [
            "timeout", "connection", "network", "dns", "resolve",
            "temporary", "rate limit", "quota", "503", "502", "500",
            "connection reset", "connection refused"
        ]):
            return True

        # API限流错误
        if any(keyword in error_str for keyword in [
            "too many requests", "rate limited", "quota exceeded"
        ]):
            return True

        return False

class DeepSeekAdapter(BaseLLMAdapter):
    """
    适配官方/OpenAI兼容接口（使用 langchain.ChatOpenAI）
    """
    def __init__(self, api_key: str, base_url: str, model_name: str, max_tokens: int, temperature: float = 0.7, timeout: Optional[int] = 600):
        super().__init__(max_retries=3, retry_delay=1.0)
        self.base_url = check_base_url(base_url)
        self.api_key = api_key
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout

        self._client = ChatOpenAI(
            model=self.model_name,
            api_key=self.api_key,
            base_url=self.base_url,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            timeout=self.timeout
        )

    def _invoke_internal(self, prompt: str) -> str:
        """内部调用方法，用于重试"""
        response = self._client.invoke(prompt)
        if not response:
            logging.warning("DeepSeekAdapter返回空响应")
            return ""
        return response.content

    def invoke(self, prompt: str) -> str:
        """调用LLM生成响应"""
        if not prompt or not prompt.strip():
            logging.warning("DeepSeekAdapter收到空提示词")
            return ""

        return self._invoke_with_retry(self._invoke_internal, prompt)

class OpenAIAdapter(BaseLLMAdapter):
    """
    适配官方/OpenAI兼容接口（使用 langchain.ChatOpenAI）
    """
    def __init__(self, api_key: str, base_url: str, model_name: str, max_tokens: int, temperature: float = 0.7, timeout: Optional[int] = 600):
        self.base_url = check_base_url(base_url)
        self.api_key = api_key
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout

        self._client = ChatOpenAI(
            model=self.model_name,
            api_key=self.api_key,
            base_url=self.base_url,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            timeout=self.timeout
        )

    def invoke(self, prompt: str) -> str:
        response = self._client.invoke(prompt)
        if not response:
            logging.warning("No response from OpenAIAdapter.")
            return ""
        return response.content

class GeminiAdapter(BaseLLMAdapter):
    """
    适配 Google Gemini (Google Generative AI) 接口
    """

    # PenBo 修复新版本google-generativeai 不支持 Client 类问题；而是使用 GenerativeModel 类来访问API
    def __init__(self, api_key: str, base_url: str, model_name: str, max_tokens: int, temperature: float = 0.7, timeout: Optional[int] = 600):
        self.api_key = api_key
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout

        # 配置API密钥
        genai.configure(api_key=self.api_key)
        
        # 创建生成模型实例
        self._model = genai.GenerativeModel(model_name=self.model_name)

    def invoke(self, prompt: str) -> str:
        try:
            # 设置生成配置
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            
            # 生成内容
            response = self._model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            if response and response.text:
                return response.text
            else:
                logging.warning("No text response from Gemini API.")
                return ""
        except Exception as e:
            logging.error(f"Gemini API 调用失败: {e}")
            return ""

class AzureOpenAIAdapter(BaseLLMAdapter):
    """
    适配 Azure OpenAI 接口（使用 langchain.ChatOpenAI）
    """
    def __init__(self, api_key: str, base_url: str, model_name: str, max_tokens: int, temperature: float = 0.7, timeout: Optional[int] = 600):
        import re
        match = re.match(r'https://(.+?)/openai/deployments/(.+?)/chat/completions\?api-version=(.+)', base_url)
        if match:
            self.azure_endpoint = f"https://{match.group(1)}"
            self.azure_deployment = match.group(2)
            self.api_version = match.group(3)
        else:
            raise ValueError("Invalid Azure OpenAI base_url format")
        
        self.api_key = api_key
        self.model_name = self.azure_deployment
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout

        self._client = AzureChatOpenAI(
            azure_endpoint=self.azure_endpoint,
            azure_deployment=self.azure_deployment,
            api_version=self.api_version,
            api_key=self.api_key,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            timeout=self.timeout
        )

    def invoke(self, prompt: str) -> str:
        response = self._client.invoke(prompt)
        if not response:
            logging.warning("No response from AzureOpenAIAdapter.")
            return ""
        return response.content

class OllamaAdapter(BaseLLMAdapter):
    """
    Ollama 同样有一个 OpenAI-like /v1/chat 接口，可直接使用 ChatOpenAI。
    """
    def __init__(self, api_key: str, base_url: str, model_name: str, max_tokens: int, temperature: float = 0.7, timeout: Optional[int] = 600):
        self.base_url = check_base_url(base_url)
        self.api_key = api_key
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout

        if self.api_key == '':
            self.api_key= 'ollama'

        self._client = ChatOpenAI(
            model=self.model_name,
            api_key=self.api_key,
            base_url=self.base_url,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            timeout=self.timeout
        )

    def invoke(self, prompt: str) -> str:
        response = self._client.invoke(prompt)
        if not response:
            logging.warning("No response from OllamaAdapter.")
            return ""
        return response.content

class MLStudioAdapter(BaseLLMAdapter):
    def __init__(self, api_key: str, base_url: str, model_name: str, max_tokens: int, temperature: float = 0.7, timeout: Optional[int] = 600):
        self.base_url = check_base_url(base_url)
        self.api_key = api_key
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout

        self._client = ChatOpenAI(
            model=self.model_name,
            api_key=self.api_key,
            base_url=self.base_url,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            timeout=self.timeout
        )

    def invoke(self, prompt: str) -> str:
        try:
            response = self._client.invoke(prompt)
            if not response:
                logging.warning("No response from MLStudioAdapter.")
                return ""
            return response.content
        except Exception as e:
            logging.error(f"ML Studio API 调用超时或失败: {e}")
            return ""

class AzureAIAdapter(BaseLLMAdapter):
    """
    适配 Azure AI Inference 接口，用于访问Azure AI服务部署的模型
    使用 azure-ai-inference 库进行API调用
    """
    def __init__(self, api_key: str, base_url: str, model_name: str, max_tokens: int, temperature: float = 0.7, timeout: Optional[int] = 600):
        # 检查Azure依赖是否可用
        ChatCompletionsClient, AzureKeyCredential, SystemMessage, UserMessage = _import_azure_components()

        if ChatCompletionsClient is None:
            raise ImportError(
                "Azure AI适配器需要安装 azure-ai-inference 包。\n"
                "请运行: pip install azure-ai-inference\n"
                "或者使用其他适配器如 OpenAI、DeepSeek 等。"
            )

        import re
        # 匹配形如 https://xxx.services.ai.azure.com/models/chat/completions?api-version=xxx 的URL
        match = re.match(r'https://(.+?)\.services\.ai\.azure\.com(?:/models)?(?:/chat/completions)?(?:\?api-version=(.+))?', base_url)
        if match:
            # endpoint需要是形如 https://xxx.services.ai.azure.com/models 的格式
            self.endpoint = f"https://{match.group(1)}.services.ai.azure.com/models"
            # 如果URL中包含api-version参数，使用它；否则使用默认值
            self.api_version = match.group(2) if match.group(2) else "2024-05-01-preview"
        else:
            raise ValueError("Invalid Azure AI base_url format. Expected format: https://<endpoint>.services.ai.azure.com/models/chat/completions?api-version=xxx")

        self.base_url = self.endpoint  # 存储处理后的endpoint URL
        self.api_key = api_key
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout

        self._client = ChatCompletionsClient(
            endpoint=self.endpoint,
            credential=AzureKeyCredential(self.api_key),
            model=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            timeout=self.timeout
        )

    def invoke(self, prompt: str) -> str:
        try:
            # 动态导入Azure组件
            _, _, SystemMessage, UserMessage = _import_azure_components()

            response = self._client.complete(
                messages=[
                    SystemMessage("You are a helpful assistant."),
                    UserMessage(prompt)
                ]
            )
            if response and response.choices:
                return response.choices[0].message.content
            else:
                logging.warning("No response from AzureAIAdapter.")
                return ""
        except Exception as e:
            logging.error(f"Azure AI Inference API 调用失败: {e}")
            return ""

# 火山引擎实现
class VolcanoEngineAIAdapter(BaseLLMAdapter):
    def __init__(self, api_key: str, base_url: str, model_name: str, max_tokens: int, temperature: float = 0.7, timeout: Optional[int] = 600):
        self.base_url = check_base_url(base_url)
        self.api_key = api_key
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout

        self._client = OpenAI(
            base_url=base_url,
            api_key=api_key,
            timeout=timeout  # 添加超时配置
        )
    def invoke(self, prompt: str) -> str:
        try:
            response = self._client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "你是DeepSeek，是一个 AI 人工智能助手"},
                    {"role": "user", "content": prompt},
                ],
                timeout=self.timeout  # 添加超时参数
            )
            if not response:
                logging.warning("No response from DeepSeekAdapter.")
                return ""
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"火山引擎API调用超时或失败: {e}")
            return ""

class SiliconFlowAdapter(BaseLLMAdapter):
    def __init__(self, api_key: str, base_url: str, model_name: str, max_tokens: int, temperature: float = 0.7, timeout: Optional[int] = 600):
        self.base_url = check_base_url(base_url)
        self.api_key = api_key
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout

        self._client = OpenAI(
            base_url=base_url,
            api_key=api_key,
            timeout=timeout  # 添加超时配置
        )
    def invoke(self, prompt: str) -> str:
        try:
            response = self._client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "你是DeepSeek，是一个 AI 人工智能助手"},
                    {"role": "user", "content": prompt},
                ],
                timeout=self.timeout  # 添加超时参数
            )
            if not response:
                logging.warning("No response from DeepSeekAdapter.")
                return ""
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"硅基流动API调用超时或失败: {e}")
            return ""
# grok實現
class GrokAdapter(BaseLLMAdapter):
    """
    适配 xAI Grok API
    """
    def __init__(self, api_key: str, base_url: str, model_name: str, max_tokens: int, temperature: float = 0.7, timeout: Optional[int] = 600):
        self.base_url = check_base_url(base_url)
        self.api_key = api_key
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout

        self._client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            timeout=self.timeout
        )

    def invoke(self, prompt: str) -> str:
        try:
            response = self._client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are Grok, created by xAI."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                timeout=self.timeout
            )
            if response and response.choices:
                return response.choices[0].message.content
            else:
                logging.warning("No response from GrokAdapter.")
                return ""
        except Exception as e:
            logging.error(f"Grok API 调用失败: {e}")
            return ""

def create_llm_adapter(
    interface_format: str,
    base_url: str,
    model_name: str,
    api_key: str,
    temperature: float,
    max_tokens: int,
    timeout: int
) -> BaseLLMAdapter:
    """
    工厂函数：根据 interface_format 返回不同的适配器实例。
    增加了参数验证和错误处理。
    """
    # 参数验证
    if not interface_format or not isinstance(interface_format, str):
        raise ValueError("interface_format 必须是非空字符串")

    if not model_name or not isinstance(model_name, str):
        raise ValueError("model_name 必须是非空字符串")

    # 验证数值参数
    if not isinstance(temperature, (int, float)) or temperature < 0 or temperature > 2:
        logging.warning(f"temperature 值 {temperature} 不在合理范围内 [0, 2]，将设为 0.7")
        temperature = 0.7

    if not isinstance(max_tokens, int) or max_tokens <= 0:
        logging.warning(f"max_tokens 值 {max_tokens} 无效，将设为 4096")
        max_tokens = 4096

    if not isinstance(timeout, int) or timeout <= 0:
        logging.warning(f"timeout 值 {timeout} 无效，将设为 600")
        timeout = 600

    fmt = interface_format.strip().lower()

    try:
        if fmt == "deepseek":
            return DeepSeekAdapter(api_key, base_url, model_name, max_tokens, temperature, timeout)
        elif fmt == "openai":
            return OpenAIAdapter(api_key, base_url, model_name, max_tokens, temperature, timeout)
        elif fmt == "azure openai":
            return AzureOpenAIAdapter(api_key, base_url, model_name, max_tokens, temperature, timeout)
        elif fmt == "azure ai":
            return AzureAIAdapter(api_key, base_url, model_name, max_tokens, temperature, timeout)
        elif fmt == "ollama":
            return OllamaAdapter(api_key, base_url, model_name, max_tokens, temperature, timeout)
        elif fmt == "ml studio":
            return MLStudioAdapter(api_key, base_url, model_name, max_tokens, temperature, timeout)
        elif fmt == "gemini":
            return GeminiAdapter(api_key, base_url, model_name, max_tokens, temperature, timeout)
        elif fmt == "阿里云百炼":
            return OpenAIAdapter(api_key, base_url, model_name, max_tokens, temperature, timeout)
        elif fmt == "火山引擎":
            return VolcanoEngineAIAdapter(api_key, base_url, model_name, max_tokens, temperature, timeout)
        elif fmt == "硅基流动":
            return SiliconFlowAdapter(api_key, base_url, model_name, max_tokens, temperature, timeout)
        elif fmt == "grok":
            return GrokAdapter(api_key, base_url, model_name, max_tokens, temperature, timeout)
        else:
            # 尝试默认使用OpenAI兼容接口
            logging.warning(f"未知的接口格式: {interface_format}，将使用OpenAI兼容接口")
            return DeepSeekAdapter(api_key, base_url, model_name, max_tokens, temperature, timeout)

    except Exception as e:
        logging.error(f"创建LLM适配器失败: {e}")
        # 返回一个基本的适配器作为后备
        try:
            return DeepSeekAdapter(api_key, base_url or "https://api.openai.com/v1",
                                 model_name or "gpt-3.5-turbo", max_tokens, temperature, timeout)
        except Exception as fallback_error:
            logging.error(f"创建后备适配器也失败: {fallback_error}")
            raise ValueError(f"无法创建任何LLM适配器: {e}")
