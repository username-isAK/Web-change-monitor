from os import getenv
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

client = Groq(api_key=getenv("GROQ_API_KEY"))

def analyze_changes(changes, url):
    """
    Uses LLM to summarize and classify detected changes
    """
    prompt = f"""
You are an AI monitoring agent.

A webpage has changed: {url}

Changes detected:
{changes}

Tasks:
1. Summarize the changes in 2–3 bullet points.
2. Classify importance as LOW, MEDIUM, or HIGH.
3. If HIGH, explain why briefly.

Respond in JSON with keys:
summary, importance, reasoning
"""

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    return completion.choices[0].message.content
