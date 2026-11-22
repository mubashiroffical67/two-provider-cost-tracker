# Two Provider Cost Tracker

Assignment 1 · Week 1

This project sends the **same prompt** to Google Gemini and Groq from one Python script. It prints each model's reply and a side-by-side comparison of API-reported input tokens, output tokens, elapsed seconds, and calculated USD cost. It also saves one result object per provider to `results.json`.

## Requirements

- Python 3.10 or newer
- [uv](https://docs.astral.sh/uv/)
- A Gemini API key from [Google AI Studio](https://aistudio.google.com/)
- A Groq API key from [Groq Console](https://console.groq.com/keys)

Both providers offer free tiers, but availability, quotas, model access, and pricing can change.

## Setup

1. Create a GitHub repository and clone it.
2. In the repository folder, create `.gitignore` and ensure `.env` is listed in it. Commit `.gitignore` before putting any real API key in a file.
3. Copy `.env.example` to `.env`.
4. Put your real keys in `.env`. Never commit or upload `.env`.
5. Check the official pricing pages and update the four `*_PRICE_PER_M` values in `.env`. Values are USD per 1 million tokens:
   - Gemini: https://ai.google.dev/gemini-api/docs/pricing
   - Groq: https://groq.com/pricing/
6. Install dependencies:

```bash
uv sync
```

## Run

```bash
uv run tracker.py "Explain artificial intelligence with three real-world examples."
```

The script calls both providers with the same prompt. It reads token counts from each API's usage metadata; it does not estimate tokens from words. The cost formula is:

```text
(input_tokens × input_price_per_m / 1,000,000)
+ (output_tokens × output_price_per_m / 1,000,000)
```

The default models are `gemini-2.5-flash` and `openai/gpt-oss-120b`. The model names are configurable in `.env` as `GEMINI_MODEL` and `GROQ_MODEL`.

## Output

- Each provider's reply is printed.
- A comparison table displays provider, input tokens, output tokens, seconds, and cost in USD.
- `results.json` is created in the project root with these fields for each provider:
  `provider`, `model`, `reply`, `input_tokens`, `output_tokens`,
  `input_price_per_m`, `output_price_per_m`, `cost_usd`, `seconds`.

Run the program with three different prompts as requested in the assignment. Each run replaces `results.json` with that run's results; save or rename a copy if you want to preserve earlier runs.

## Google Colab quick test

The ZIP also contains `colab_test.ipynb`. Upload it to Google Colab, open it, and run its single code cell. It installs the packages, asks for the two API keys privately, calls both providers, prints the comparison, and creates a downloadable `results.json`.

## What I learned

This project demonstrates how to call two LLM providers from Python, compare their API-reported token usage and response time, and calculate the cost of each request using per-million-token pricing. Different providers and models can return different token counts and response times for the same prompt.

## Security

Never commit `.env`, paste API keys into GitHub or Google Classroom, or include keys in screenshots. The assignment grading checks the entire Git history for secrets; deleting a key in a later commit does not remove it from earlier history. If a key was committed, revoke it and create a new one.
