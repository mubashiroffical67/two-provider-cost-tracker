# ============================================================
# Two Provider Cost Tracker - Google Colab one-cell test
# AI Assistance: ChatGPT was used for coding assistance,
# understanding, debugging, and project development.
# ============================================================

!pip -q install -U google-genai groq

import json
import time
from getpass import getpass
from google import genai
from groq import Groq
from IPython.display import display, FileLink

print("Enter your API keys. They will be hidden while typing.")
GEMINI_API_KEY = getpass("Gemini API key: ").strip()
GROQ_API_KEY = getpass("Groq API key: ").strip()

if not GEMINI_API_KEY:
    raise ValueError("Gemini API key is missing.")
if not GROQ_API_KEY:
    raise ValueError("Groq API key is missing.")

# You can replace the prompt below with any test prompt.
PROMPT = "Explain artificial intelligence with three real-world examples in simple English."

# Model IDs can change as provider catalogs evolve. If a model is unavailable,
# update its name to one enabled for your API account.
GEMINI_MODEL = "gemini-2.5-flash"
GROQ_MODEL = "openai/gpt-oss-120b"

# USD per 1 million tokens. Verify current prices on official pricing pages.
PRICES = {
    "gemini": {"input": 0.30, "output": 2.50},
    "groq": {"input": 0.15, "output": 0.60},
}

def calculate_cost(provider, input_tokens, output_tokens):
    return (
        input_tokens * PRICES[provider]["input"] / 1_000_000
        + output_tokens * PRICES[provider]["output"] / 1_000_000
    )

gemini_client = genai.Client(api_key=GEMINI_API_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)
results = []

print("\nCalling Gemini...")
start = time.perf_counter()
gemini_response = gemini_client.models.generate_content(
    model=GEMINI_MODEL, contents=PROMPT
)
gemini_seconds = time.perf_counter() - start
gemini_usage = gemini_response.usage_metadata
if (gemini_usage is None or gemini_usage.prompt_token_count is None
        or gemini_usage.candidates_token_count is None):
    raise RuntimeError("Gemini did not return complete token usage data.")

gemini_input = int(gemini_usage.prompt_token_count)
gemini_output = int(gemini_usage.candidates_token_count)
results.append({
    "provider": "gemini",
    "model": GEMINI_MODEL,
    "reply": gemini_response.text or "",
    "input_tokens": gemini_input,
    "output_tokens": gemini_output,
    "input_price_per_m": PRICES["gemini"]["input"],
    "output_price_per_m": PRICES["gemini"]["output"],
    "cost_usd": calculate_cost("gemini", gemini_input, gemini_output),
    "seconds": round(gemini_seconds, 3),
})

print("Calling Groq...")
start = time.perf_counter()
groq_response = groq_client.chat.completions.create(
    model=GROQ_MODEL,
    messages=[{"role": "user", "content": PROMPT}],
)
groq_seconds = time.perf_counter() - start
groq_usage = groq_response.usage
if groq_usage is None:
    raise RuntimeError("Groq did not return token usage data.")

groq_input = int(groq_usage.prompt_tokens)
groq_output = int(groq_usage.completion_tokens)
results.append({
    "provider": "groq",
    "model": GROQ_MODEL,
    "reply": groq_response.choices[0].message.content or "",
    "input_tokens": groq_input,
    "output_tokens": groq_output,
    "input_price_per_m": PRICES["groq"]["input"],
    "output_price_per_m": PRICES["groq"]["output"],
    "cost_usd": calculate_cost("groq", groq_input, groq_output),
    "seconds": round(groq_seconds, 3),
})

for item in results:
    print("\n" + "=" * 65)
    print(item["provider"].upper(), "RESPONSE")
    print("=" * 65)
    print(item["reply"])

print("\nCOMPARISON")
print(f"{'Provider':<12}{'Input':>10}{'Output':>10}{'Seconds':>12}{'Cost USD':>15}")
print("-" * 59)
for item in results:
    print(
        f"{item['provider']:<12}{item['input_tokens']:>10}"
        f"{item['output_tokens']:>10}{item['seconds']:>12.3f}"
        f"{item['cost_usd']:>15.8f}"
    )

with open("results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=4, ensure_ascii=False)

print("\nDone! results.json has been created.")
display(FileLink("results.json"))
