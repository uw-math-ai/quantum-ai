import os
import sys
import ollama


def _get_arg_value(flag: str) -> str | None:
    if flag in sys.argv:
        idx = sys.argv.index(flag)
        if idx + 1 < len(sys.argv):
            return sys.argv[idx + 1]
    return None


def main() -> int:
    model = _get_arg_value("--model") or os.getenv("OLLAMA_MODEL", "ministral-3:8b")
    host = _get_arg_value("--host") or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    client = ollama.Client(host=host)

    try:
        models = client.list().get("models", [])
    except Exception as exc:
        print(f"Failed to reach Ollama at {host}: {exc}")
        return 1

    names = {item.get("name") for item in models}
    if model not in names:
        print(f"Model '{model}' not found locally. Pulling...")
        client.pull(model)

    reply = client.chat(
        model=model,
        messages=[{"role": "user", "content": "Respond with 'ok' only."}],
    )
    content = reply.get("message", {}).get("content", "").strip()
    print(f"Ollama ready ({model}) -> {content or 'no response'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
