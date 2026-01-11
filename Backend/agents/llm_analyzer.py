from os import getenv
from groq import Groq
from dotenv import load_dotenv
import json
import re

load_dotenv()

client = Groq(api_key=getenv("GROQ_API_KEY"))

def analyze_changes(changes, url):
    prompt = f"""
You are an AI monitoring agent.

A webpage has changed: {url}

Changes detected:
{changes}

Tasks:
1. Summarize the changes in 2–3 bullet points.
2. Classify importance as LOW, MEDIUM, or HIGH.
3. If HIGH, explain why briefly.

Respond ONLY with valid JSON.
No markdown. No extra text.
Keys: summary, importance, reasoning
"""

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    raw = completion.choices[0].message.content.strip()

    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise ValueError("LLM did not return valid JSON")

    return json.loads(match.group())
