
"""
Two Provider Cost Tracker
Sends the same prompt to Gemini and Groq,
reads token usage, calculates cost, and saves results.json.
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from groq import Groq


def required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(
            f"Missing {name}. Add it to your .env file."
        )
    return value


def price(provider: str, kind: str) -> float:
    key = f"{provider.upper()}_{kind.upper()}_PRICE_PER_M"
    raw = os.getenv(key, "").strip()

    if not raw:
        raise RuntimeError(f"Missing {key} in .env.")

    try:
        value = float(raw)
    except ValueError as exc:
        raise RuntimeError(f"{key} must be a number.") from exc

    if value < 0:
        raise RuntimeError(f"{key} cannot be negative.")

    return value


def calculate_cost(
    input_tokens: int,
    output_tokens: int,
    input_price_per_m: float,
    output_price_per_m: float,
) -> float:
    return (
        input_tokens * input_price_per_m / 1_000_000
        + output_tokens * output_price_per_m / 1_000_000
    )


def call_gemini(prompt: str) -> dict:
    api_key = required_env("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()

    client = genai.Client(api_key=api_key)

    start = time.perf_counter()
    response = client.models.generate_content(
        model=model,
        contents=prompt,
    )
    seconds = time.perf_counter() - start

    usage = response.usage_metadata

    if (
        usage is None
        or usage.prompt_token_count is None
        or usage.candidates_token_count is None
    ):
        raise RuntimeError("Gemini did not return complete token usage.")

    input_tokens = int(usage.prompt_token_count)
    output_tokens = int(usage.candidates_token_count)

    input_price = price("gemini", "input")
    output_price = price("gemini", "output")

    return {
        "provider": "gemini",
        "model": model,
        "reply": response.text or "",
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "input_price_per_m": input_price,
        "output_price_per_m": output_price,
        "cost_usd": calculate_cost(
            input_tokens,
            output_tokens,
            input_price,
            output_price,
        ),
        "seconds": round(seconds, 3),
    }


def call_groq(prompt: str) -> dict:
    api_key = required_env("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b").strip()

    client = Groq(api_key=api_key)

    start = time.perf_counter()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ],
    )
    seconds = time.perf_counter() - start

    usage = response.usage

    if usage is None:
        raise RuntimeError("Groq did not return token usage.")

    input_tokens = int(usage.prompt_tokens)
    output_tokens = int(usage.completion_tokens)

    input_price = price("groq", "input")
    output_price = price("groq", "output")

    return {
        "provider": "groq",
        "model": model,
        "reply": response.choices[0].message.content or "",
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "input_price_per_m": input_price,
        "output_price_per_m": output_price,
        "cost_usd": calculate_cost(
            input_tokens,
            output_tokens,
            input_price,
            output_price,
        ),
        "seconds": round(seconds, 3),
    }


def print_results(results: list[dict]) -> None:
    for item in results:
        print("\n" + "=" * 70)
        print(f"{item['provider'].upper()} ({item['model']})")
        print("=" * 70)
        print(item["reply"])

    print("\n" + "=" * 78)
    print("COMPARISON")
    print("=" * 78)

    print(
        f"{'Provider':<12}"
        f"{'Input tokens':>14}"
        f"{'Output tokens':>15}"
        f"{'Seconds':>12}"
        f"{'Cost USD':>15}"
    )
    print("-" * 78)

    for item in results:
        print(
            f"{item['provider']:<12}"
            f"{item['input_tokens']:>14}"
            f"{item['output_tokens']:>15}"
            f"{item['seconds']:>12.3f}"
            f"{item['cost_usd']:>15.8f}"
        )


def main() -> int:
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Compare Gemini and Groq using the same prompt."
    )
    parser.add_argument(
        "prompt",
        nargs="+",
        help='Prompt to send, e.g. "Explain AI simply"',
    )

    args = parser.parse_args()
    prompt = " ".join(args.prompt).strip()

    results = []
    errors = []

    for provider, function in (
        ("gemini", call_gemini),
        ("groq", call_groq),
    ):
        try:
            print(f"Calling {provider}...")
            results.append(function(prompt))
        except Exception as exc:
            errors.append(f"{provider}: {exc}")

    if errors:
        for message in errors:
            print(f"ERROR - {message}", file=sys.stderr)

        if len(results) != 2:
            print(
                "Both providers must succeed. No comparison was saved.",
                file=sys.stderr,
            )
            return 1

    print_results(results)

    output_path = Path("results.json")
    output_path.write_text(
        json.dumps(results, indent=4, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"\nSaved results to: {output_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
