"""
LLM Service for DeepContext RAG system.

Uses Ollama for local LLM inference with configurable models.
Supports both sync and streaming responses.
"""

import os
from typing import Generator, List, Optional

import ollama
from pydantic import BaseModel


class LLMConfig(BaseModel):
    """Configuration for LLM service."""

    model: str = "llama3"
    temperature: float = 0.7
    max_tokens: int = 2048
    ollama_host: Optional[str] = None


SYSTEM_PROMPT = """你是一个私人知识库助手。请仅根据提供的上下文内容回答问题。

重要规则：
1. 只能使用上下文中的信息来回答问题
2. 如果上下文不包含答案，请直说"根据现有资料，我无法回答这个问题"
3. 不要编造或推测上下文中没有的信息
4. 回答时可以引用上下文中的具体内容
5. 保持回答简洁、准确、有帮助"""


def build_rag_prompt(query: str, contexts: List[str]) -> str:
    """Build RAG prompt with contexts."""
    context_str = "\n\n---\n\n".join(
        [f"[片段 {i + 1}]\n{ctx}" for i, ctx in enumerate(contexts)]
    )

    return f"""请根据以下上下文回答问题。

## 上下文内容

{context_str}

## 用户问题

{query}

## 回答"""


class LLMService:
    """
    Local LLM service using Ollama.

    Supports configurable models (llama3, qwen2, etc.)
    """

    def __init__(self, config: Optional[LLMConfig] = None):
        """
        Initialize LLM service.

        Args:
            config: LLM configuration options
        """
        self.config = config or LLMConfig()

        # Override from environment variables
        self.config.model = os.environ.get("LLM_MODEL", self.config.model)
        ollama_host = os.environ.get("OLLAMA_HOST", self.config.ollama_host)

        # Initialize Ollama client
        if ollama_host:
            self.client = ollama.Client(host=ollama_host)
        else:
            self.client = ollama.Client()

        print(f"[LLMService] Initialized with model: {self.config.model}")

    def generate_answer(
        self,
        query: str,
        contexts: List[str],
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Generate answer using RAG context (non-streaming).

        Args:
            query: User's question
            contexts: List of relevant text chunks from vector search
            system_prompt: Optional custom system prompt

        Returns:
            Generated answer from LLM
        """
        if not contexts:
            return "没有找到相关的上下文信息，无法回答您的问题。"

        user_message = build_rag_prompt(query, contexts)
        sys_prompt = system_prompt or SYSTEM_PROMPT

        try:
            response = self.client.chat(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": user_message},
                ],
                options={
                    "temperature": self.config.temperature,
                    "num_predict": self.config.max_tokens,
                },
            )

            return response["message"]["content"]

        except ollama.ResponseError as e:
            error_msg = f"Ollama API error: {e}"
            print(f"[LLMService] {error_msg}")
            raise RuntimeError(error_msg)

        except Exception as e:
            error_msg = f"LLM generation failed: {e}"
            print(f"[LLMService] {error_msg}")
            raise RuntimeError(error_msg)

    def generate_answer_stream(
        self,
        query: str,
        contexts: List[str],
        system_prompt: Optional[str] = None,
    ) -> Generator[str, None, None]:
        """
        Generate answer using RAG context (streaming).

        Args:
            query: User's question
            contexts: List of relevant text chunks from vector search
            system_prompt: Optional custom system prompt

        Yields:
            Chunks of generated answer text
        """
        if not contexts:
            yield "没有找到相关的上下文信息，无法回答您的问题。"
            return

        user_message = build_rag_prompt(query, contexts)
        sys_prompt = system_prompt or SYSTEM_PROMPT

        try:
            stream = self.client.chat(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": user_message},
                ],
                options={
                    "temperature": self.config.temperature,
                    "num_predict": self.config.max_tokens,
                },
                stream=True,
            )

            for chunk in stream:
                content = chunk.get("message", {}).get("content", "")
                if content:
                    yield content

        except ollama.ResponseError as e:
            error_msg = f"Ollama API error: {e}"
            print(f"[LLMService] {error_msg}")
            raise RuntimeError(error_msg)

        except Exception as e:
            error_msg = f"LLM generation failed: {e}"
            print(f"[LLMService] {error_msg}")
            raise RuntimeError(error_msg)

    def check_model_available(self) -> bool:
        """Check if configured model is available in Ollama."""
        try:
            models = self.client.list()
            model_names = [m["name"].split(":")[0] for m in models.get("models", [])]
            return self.config.model in model_names
        except Exception as e:
            print(f"[LLMService] Error checking models: {e}")
            return False

    def get_available_models(self) -> List[str]:
        """Get list of available models from Ollama."""
        try:
            models = self.client.list()
            return [m["name"] for m in models.get("models", [])]
        except Exception as e:
            print(f"[LLMService] Error listing models: {e}")
            return []


# Global instance
_llm_service: Optional[LLMService] = None


def get_llm_service(config: Optional[LLMConfig] = None) -> LLMService:
    """
    Get or create global LLMService instance.

    Args:
        config: Optional LLM configuration

    Returns:
        LLMService instance
    """
    global _llm_service

    if _llm_service is None:
        _llm_service = LLMService(config=config)

    return _llm_service
