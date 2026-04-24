import os
from anthropic import AsyncAnthropic
from collections.abc import AsyncGenerator

client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

MODEL = os.getenv("CLAUDE_MODEL")


def build_prompt(question: str, chunks: list[dict]) -> str:
    """
    Assemble retrieved chunks and the user's question into a prompt.

    Formats each chunk as a numbered context block so Claude can reference
    specific sections. The instruction to answer only from context prevents
    hallucination.

    Args:
        question: The user's plain text question.
        chunks: Retrieved chunks from search_chunks(), each with a "text" key.

    Returns:
        A formatted prompt string ready to send to Claude.
    """
    context_blocks = "\n\n".join(
        f"[{i + 1}] {chunk['text']}" for i, chunk in enumerate(chunks)
    )

    return (
        f"Answer the question using only the context below. "
        f"If the answer is not in the context, say: "
        f"'I could not find the answer in the provided document.'\n\n"
        f"Context:\n{context_blocks}\n\n"
        f"Question: {question}"
    )


async def stream_answer(question: str, chunks: list[dict]) -> AsyncGenerator[str, None]:
    """
    Stream Claude's answer token by token.

    Sends the assembled prompt to the Anthropic API with streaming enabled
    and yields each text token as it arrives. The caller receives tokens
    one at a time rather than waiting for the full response.

    Args:
        question: The user's plain text question.
        chunks: Retrieved chunks from search_chunks() to use as context.

    Yields:
        Individual text tokens from Claude's response as they stream in.
    """
    prompt = build_prompt(question, chunks)

    async with client.messages.stream(
        model=MODEL,
        max_tokens=1024,
        system=(
            "You are a helpful document assistant. "
            "Answer only from the provided context. "
            "Be concise and accurate."
        ),
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        async for text in stream.text_stream:
            yield text
