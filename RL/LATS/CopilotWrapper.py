"""
CopilotWrapper: llama_index LLM adapter for GitHub Copilot SDK.

Wraps CopilotClient to work as a llama_index CustomLLM, enabling use
of Copilot models (including ollama) in llama_index applications.
"""

import os
import asyncio
from typing import Any, Callable, Optional, Sequence, AsyncGenerator
from dotenv import load_dotenv

from llama_index.core.llms import (
    CustomLLM,
    CompletionResponse,
    CompletionResponseGen,
    LLMMetadata,
    CompletionResponseAsyncGen,
    ChatResponse,
    ChatResponseGen,
    ChatResponseAsyncGen,
)
from llama_index.core.llms.callbacks import llm_completion_callback, llm_chat_callback
from llama_index.core.base.llms.types import ChatMessage, MessageRole

from copilot import CopilotClient
from copilot.types import Tool, Attachment
from copilot.generated.session_events import SessionEventType, SessionEvent

load_dotenv()


class CopilotWrapper(CustomLLM):
    """
    Wraps GitHub Copilot SDK as a llama_index CustomLLM.
    
    Supports:
    - Standard LLM models (gpt-4.1, claude-opus-4.6, etc.)
    - Ollama models via "ollama:model-name" or "ollama/model-name"
    - Tools/function calling
    - System messages
    - Streaming and non-streaming completions
    
    Example:
        >>> llm = CopilotWrapper(model="gpt-4.1", temperature=0.7)
        >>> response = llm.complete("What is 2+2?")
        >>> print(response.text)
        
        >>> # Using ollama
        >>> llm = CopilotWrapper(model="ollama:ministral-3:8b")
        >>> response = llm.complete("Explain quantum entanglement")
    """

    model: str = "gpt-4.1"
    temperature: float = 0.2
    max_tokens: int = 2048
    system_message: str = ""
    tools: list[Tool] = []
    timeout: Optional[int] = 60
    
    def __init__(
        self,
        model: str = "gpt-4.1",
        temperature: float = 0.2,
        max_tokens: int = 2048,
        system_message: str = "",
        tools: Optional[list[Tool]] = None,
        timeout: Optional[int] = 60,
        **kwargs: Any,
    ) -> None:
        """
        Initialize CopilotWrapper.
        
        Args:
            model: Model name (e.g., "gpt-4.1", "claude-opus-4.6", "ollama:ministral-3:8b")
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            system_message: System prompt/instructions
            tools: List of Copilot tools for function calling
            timeout: Request timeout in seconds (None for no timeout)
            **kwargs: Additional arguments passed to parent
        """
        super().__init__(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            system_message=system_message,
            tools=tools or [],
            timeout=timeout,
            **kwargs,
        )

    @classmethod
    def class_name(cls) -> str:
        """Return class name for serialization."""
        return "CopilotWrapper"

    @property
    def metadata(self) -> LLMMetadata:
        """Return LLM metadata."""
        # Determine context window based on model
        context_window = 128000  # default for most modern models
        if "gpt-4" in self.model.lower():
            context_window = 128000
        elif "claude" in self.model.lower():
            context_window = 200000
        elif "gemini" in self.model.lower():
            context_window = 1000000
        elif "ollama" in self.model.lower():
            context_window = 32768  # conservative default for ollama
            
        return LLMMetadata(
            context_window=context_window,
            num_output=self.max_tokens,
            model_name=self.model,
            is_chat_model=True,
            is_function_calling_model=len(self.tools) > 0,
        )

    def _resolve_model_and_provider(self, model: str) -> tuple[str, dict | None]:
        """
        Parse model string and return resolved model name and optional provider config.
        
        Supports:
        - "ollama", "ollama:", "ollama/" -> uses OLLAMA_MODEL env var
        - "ollama:model-name" -> uses "model-name"
        - "ollama/model-name" -> uses "model-name"
        - other -> returns as-is with no provider
        """
        if model.startswith("ollama"):
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
            if model in {"ollama", "ollama:", "ollama/"}:
                resolved_model = os.getenv("OLLAMA_MODEL", "ministral-3:8b")
            elif model.startswith("ollama:"):
                resolved_model = model.split(":", 1)[1].strip()
            else:
                resolved_model = model.split("/", 1)[1].strip()

            provider = {
                "type": "openai",
                "base_url": f"{base_url}/v1",
            }
            return resolved_model, provider

        return model, None

    async def _acomplete_copilot(
        self,
        prompt: str,
        attachments: Optional[list[Attachment | dict]] = None,
    ) -> str:
        """
        Core async completion method using CopilotClient.
        
        Args:
            prompt: The prompt text
            attachments: Optional list of attachments
            
        Returns:
            The completion text from the model
        """
        client = CopilotClient({"auto_start": True})
        try:
            resolved_model, provider = self._resolve_model_and_provider(self.model)
            
            session_config = {
                "model": resolved_model,
                "tools": self.tools,
            }
            
            if self.system_message:
                session_config["system_message"] = {
                    "content": self.system_message,
                }
            
            if provider:
                session_config["provider"] = provider

            session = await client.create_session(session_config)

            response = ""

            def handle_event(event: SessionEvent):
                nonlocal response
                if event.type == SessionEventType.ASSISTANT_MESSAGE:
                    if event.data.content:
                        response = event.data.content or ""

            session.on(handle_event)

            await session.send_and_wait(
                {"prompt": prompt, "attachments": attachments or []},
                timeout=self.timeout
            )

            return response
        finally:
            await client.stop()

    async def _astream_copilot(
        self,
        prompt: str,
        attachments: Optional[list[Attachment | dict]] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Core async streaming completion method using CopilotClient.
        
        Args:
            prompt: The prompt text
            attachments: Optional list of attachments
            
        Yields:
            Text chunks from the streaming response
        """
        client = CopilotClient({"auto_start": True})
        try:
            resolved_model, provider = self._resolve_model_and_provider(self.model)
            
            session_config = {
                "model": resolved_model,
                "tools": self.tools,
            }
            
            if self.system_message:
                session_config["system_message"] = {
                    "content": self.system_message,
                }
            
            if provider:
                session_config["provider"] = provider

            session = await client.create_session(session_config)

            # Queue to hold streamed chunks
            chunk_queue: asyncio.Queue[str | None] = asyncio.Queue()

            def handle_event(event: SessionEvent):
                if event.type == SessionEventType.ASSISTANT_MESSAGE:
                    if event.data.content:
                        # Put chunk in queue (non-blocking)
                        asyncio.create_task(chunk_queue.put(event.data.content))

            session.on(handle_event)

            # Start the request in background
            async def _send():
                try:
                    await session.send_and_wait(
                        {"prompt": prompt, "attachments": attachments or []},
                        timeout=self.timeout
                    )
                finally:
                    # Signal completion
                    await chunk_queue.put(None)

            send_task = asyncio.create_task(_send())

            # Yield chunks as they arrive
            while True:
                chunk = await chunk_queue.get()
                if chunk is None:
                    break
                yield chunk

            # Ensure send task completes
            await send_task

        finally:
            await client.stop()

    @llm_completion_callback()
    def complete(
        self,
        prompt: str,
        formatted: bool = False,
        **kwargs: Any,
    ) -> CompletionResponse:
        """
        Synchronous completion.
        
        Args:
            prompt: The prompt text
            formatted: Whether prompt is pre-formatted (ignored)
            **kwargs: Additional arguments (ignored)
            
        Returns:
            CompletionResponse with the generated text
        """
        response_text = asyncio.run(self._acomplete_copilot(prompt))
        return CompletionResponse(text=response_text)

    def stream_complete(
        self,
        prompt: str,
        formatted: bool = False,
        **kwargs: Any,
    ) -> CompletionResponseGen:
        """
        Synchronous streaming completion.
        
        Args:
            prompt: The prompt text
            formatted: Whether prompt is pre-formatted (ignored)
            **kwargs: Additional arguments (ignored)
            
        Yields:
            CompletionResponse objects with incremental text
        """
        async def _async_gen():
            async for chunk in self._astream_copilot(prompt):
                yield CompletionResponse(text=chunk, delta=chunk)

        # Run async generator in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            gen = _async_gen()
            while True:
                try:
                    yield loop.run_until_complete(gen.__anext__())
                except StopAsyncIteration:
                    break
        finally:
            loop.close()

    @llm_completion_callback()
    async def acomplete(
        self,
        prompt: str,
        formatted: bool = False,
        **kwargs: Any,
    ) -> CompletionResponse:
        """
        Async completion.
        
        Args:
            prompt: The prompt text
            formatted: Whether prompt is pre-formatted (ignored)
            **kwargs: Additional arguments (ignored)
            
        Returns:
            CompletionResponse with the generated text
        """
        response_text = await self._acomplete_copilot(prompt)
        return CompletionResponse(text=response_text)

    async def astream_complete(
        self,
        prompt: str,
        formatted: bool = False,
        **kwargs: Any,
    ) -> CompletionResponseAsyncGen:
        """
        Async streaming completion.
        
        Args:
            prompt: The prompt text
            formatted: Whether prompt is pre-formatted (ignored)
            **kwargs: Additional arguments (ignored)
            
        Yields:
            CompletionResponse objects with incremental text
        """
        async for chunk in self._astream_copilot(prompt):
            yield CompletionResponse(text=chunk, delta=chunk)

    @llm_chat_callback()
    def chat(
        self,
        messages: Sequence[ChatMessage],
        **kwargs: Any,
    ) -> ChatResponse:
        """
        Synchronous chat completion.
        
        Args:
            messages: List of ChatMessage objects
            **kwargs: Additional arguments (ignored)
            
        Returns:
            ChatResponse with the assistant's reply
        """
        # Convert messages to a prompt
        # System messages are handled separately via self.system_message
        prompt_parts = []
        for msg in messages:
            if msg.role == MessageRole.USER:
                prompt_parts.append(msg.content)
            elif msg.role == MessageRole.ASSISTANT:
                # Include for context if needed
                prompt_parts.append(f"Assistant: {msg.content}")
            elif msg.role == MessageRole.SYSTEM and not self.system_message:
                # Use first system message if no system_message set
                self.system_message = msg.content
        
        prompt = "\n\n".join(prompt_parts)
        completion = self.complete(prompt)
        return ChatResponse(
            message=ChatMessage(role=MessageRole.ASSISTANT, content=completion.text),
            raw=completion.raw,
        )

    def stream_chat(
        self,
        messages: Sequence[ChatMessage],
        **kwargs: Any,
    ) -> ChatResponseGen:
        """
        Synchronous streaming chat completion.
        
        Args:
            messages: List of ChatMessage objects
            **kwargs: Additional arguments (ignored)
            
        Yields:
            ChatResponse objects with incremental text
        """
        # Convert messages to a prompt
        prompt_parts = []
        for msg in messages:
            if msg.role == MessageRole.USER:
                prompt_parts.append(msg.content)
            elif msg.role == MessageRole.ASSISTANT:
                prompt_parts.append(f"Assistant: {msg.content}")
            elif msg.role == MessageRole.SYSTEM and not self.system_message:
                self.system_message = msg.content
        
        prompt = "\n\n".join(prompt_parts)
        for completion in self.stream_complete(prompt):
            yield ChatResponse(
                message=ChatMessage(role=MessageRole.ASSISTANT, content=completion.text),
                delta=completion.delta,
                raw=completion.raw,
            )

    @llm_chat_callback()
    async def achat(
        self,
        messages: Sequence[ChatMessage],
        **kwargs: Any,
    ) -> ChatResponse:
        """
        Async chat completion.
        
        Args:
            messages: List of ChatMessage objects
            **kwargs: Additional arguments (ignored)
            
        Returns:
            ChatResponse with the assistant's reply
        """
        # Convert messages to a prompt
        prompt_parts = []
        for msg in messages:
            if msg.role == MessageRole.USER:
                prompt_parts.append(msg.content)
            elif msg.role == MessageRole.ASSISTANT:
                prompt_parts.append(f"Assistant: {msg.content}")
            elif msg.role == MessageRole.SYSTEM and not self.system_message:
                self.system_message = msg.content
        
        prompt = "\n\n".join(prompt_parts)
        completion = await self.acomplete(prompt)
        return ChatResponse(
            message=ChatMessage(role=MessageRole.ASSISTANT, content=completion.text),
            raw=completion.raw,
        )

    async def astream_chat(
        self,
        messages: Sequence[ChatMessage],
        **kwargs: Any,
    ) -> ChatResponseAsyncGen:
        """
        Async streaming chat completion.
        
        Args:
            messages: List of ChatMessage objects
            **kwargs: Additional arguments (ignored)
            
        Yields:
            ChatResponse objects with incremental text
        """
        # Convert messages to a prompt
        prompt_parts = []
        for msg in messages:
            if msg.role == MessageRole.USER:
                prompt_parts.append(msg.content)
            elif msg.role == MessageRole.ASSISTANT:
                prompt_parts.append(f"Assistant: {msg.content}")
            elif msg.role == MessageRole.SYSTEM and not self.system_message:
                self.system_message = msg.content
        
        prompt = "\n\n".join(prompt_parts)
        async for completion in self.astream_complete(prompt):
            yield ChatResponse(
                message=ChatMessage(role=MessageRole.ASSISTANT, content=completion.text),
                delta=completion.delta,
                raw=completion.raw,
            )


# Example usage
if __name__ == "__main__":
    # Basic usage
    llm = CopilotWrapper(model="gpt-4.1", temperature=0.7)
    
    # Sync completion
    response = llm.complete("What is the capital of France?")
    print(f"Response: {response.text}")
    
    # Async completion
    async def test_async():
        response = await llm.acomplete("Explain quantum computing in one sentence.")
        print(f"Async response: {response.text}")
    
    asyncio.run(test_async())
    
    # Streaming
    print("\nStreaming response:")
    for chunk in llm.stream_complete("Count from 1 to 5."):
        print(chunk.delta, end="", flush=True)
    print()
    
    # Chat
    from llama_index.core.base.llms.types import ChatMessage, MessageRole
    
    messages = [
        ChatMessage(role=MessageRole.SYSTEM, content="You are a helpful assistant."),
        ChatMessage(role=MessageRole.USER, content="What is 2+2?"),
    ]
    response = llm.chat(messages)
    print(f"\nChat response: {response.message.content}")
    
    # Ollama example (if available)
    # ollama_llm = CopilotWrapper(model="ollama:ministral-3:8b")
    # response = ollama_llm.complete("Explain machine learning briefly.")
    # print(f"Ollama response: {response.text}")
