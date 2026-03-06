"""
Test script for CopilotWrapper with llama_index.

Demonstrates basic usage and integration with quantum circuit generation tasks.
"""

import asyncio
from CopilotWrapper import CopilotWrapper
from llama_index.core.base.llms.types import ChatMessage, MessageRole


def test_basic_completion():
    """Test basic synchronous completion."""
    print("=" * 60)
    print("Test 1: Basic Completion")
    print("=" * 60)
    
    llm = CopilotWrapper(
        model="gpt-4.1",
        temperature=0.7,
        max_tokens=500,
        timeout=180  # Increase timeout to 3 minutes
    )
    
    prompt = "What is quantum error correction?"
    response = llm.complete(prompt)
    print(f"Prompt: {prompt}")
    print(f"Response: {response.text}\n")


def test_streaming():
    """Test streaming completion."""
    print("=" * 60)
    print("Test 2: Streaming Completion")
    print("=" * 60)
    
    llm = CopilotWrapper(
        model="gpt-4.1",
        temperature=0.5,
    )
    
    prompt = "List the steps to create a quantum circuit."
    print(f"Prompt: {prompt}")
    print("Response: ", end="", flush=True)
    
    for chunk in llm.stream_complete(prompt):
        print(chunk.delta, end="", flush=True)
    print("\n")


def test_chat():
    """Test chat interface."""
    print("=" * 60)
    print("Test 3: Chat Interface")
    print("=" * 60)
    
    llm = CopilotWrapper(
        model="gpt-4.1",
        temperature=0.7,
        system_message="You are a quantum computing expert specializing in error correction."
    )
    
    messages = [
        ChatMessage(
            role=MessageRole.USER,
            content="Explain the [[5,1,3]] quantum code in one sentence."
        ),
    ]
    
    response = llm.chat(messages)
    print(f"User: {messages[0].content}")
    print(f"Assistant: {response.message.content}\n")


async def test_async_completion():
    """Test async completion."""
    print("=" * 60)
    print("Test 4: Async Completion")
    print("=" * 60)
    
    llm = CopilotWrapper(
        model="gpt-4.1",
        temperature=0.5,
    )
    
    prompt = "What are stabilizer codes?"
    response = await llm.acomplete(prompt)
    print(f"Prompt: {prompt}")
    print(f"Response: {response.text}\n")


async def test_async_streaming():
    """Test async streaming."""
    print("=" * 60)
    print("Test 5: Async Streaming")
    print("=" * 60)
    
    llm = CopilotWrapper(
        model="gpt-4.1",
        temperature=0.5,
    )
    
    prompt = "What is the Stim library?"
    print(f"Prompt: {prompt}")
    print("Response: ", end="", flush=True)
    
    async for chunk in llm.astream_complete(prompt):
        print(chunk.delta, end="", flush=True)
    print("\n")


def test_ollama():
    """Test with Ollama (if available)."""
    print("=" * 60)
    print("Test 6: Ollama Model (Optional)")
    print("=" * 60)
    
    try:
        llm = CopilotWrapper(
            model="ollama:ministral-3:8b",
            temperature=0.7,
        )
        
        prompt = "What is quantum entanglement?"
        response = llm.complete(prompt)
        print(f"Prompt: {prompt}")
        print(f"Response: {response.text}\n")
    except Exception as e:
        print(f"Ollama test skipped (not available or error): {e}\n")


def test_circuit_generation_prompt():
    """Test a quantum circuit generation prompt."""
    print("=" * 60)
    print("Test 7: Quantum Circuit Generation")
    print("=" * 60)
    
    llm = CopilotWrapper(
        model="gpt-4.1",
        temperature=0.3,
        system_message=(
            "You are an expert in quantum error correction circuits. "
            "Generate Stim circuit code to prepare stabilizer states."
        )
    )
    
    stabilizers = ["XZZXI", "IXZZX", "XIXZZ", "ZXIXZ"]
    stabilizers_str = ", ".join(stabilizers)
    
    prompt = f"""Generate a Stim circuit to prepare the stabilizer state defined by: {stabilizers_str}

The circuit should:
1. Initialize qubits in |0⟩
2. Apply gates to prepare the target state
3. Be as shallow as possible

Return only the Stim circuit code."""
    
    print(f"Stabilizers: {stabilizers_str}")
    print("\nGenerating circuit...\n")
    
    response = llm.complete(prompt)
    print("Generated Circuit:")
    print(response.text)
    print()


def main():
    """Run all tests."""
    print("\n🔬 CopilotWrapper Test Suite 🔬\n")
    
    # Synchronous tests
    test_basic_completion()
    test_streaming()
    test_chat()
    test_circuit_generation_prompt()
    test_ollama()
    
    # Async tests
    async def run_async_tests():
        await test_async_completion()
        await test_async_streaming()
    
    asyncio.run(run_async_tests())
    
    print("=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
