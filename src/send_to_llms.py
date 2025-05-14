import psycopg2
from src.config import DB_CONFIG, GROK_API_KEY, CLAUDE_API_KEY
import requests
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT

# Initialize Anthropic client for Claude
anthropic = Anthropic(api_key=CLAUDE_API_KEY)

# Connect to PostgreSQL database
conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

# Query 1: Total counts
cur.execute("SELECT COUNT(*) FROM pulses")
total_pulses = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM indicators")
total_indicators = cur.fetchone()[0]

# Query 2: Indicator type distribution
cur.execute("SELECT type, COUNT(*) as count FROM indicators GROUP BY type ORDER BY count DESC")
indicator_types = cur.fetchall()

# Query 3: Top 5 targeted countries
cur.execute("""
    SELECT country, COUNT(*) as count
    FROM (SELECT jsonb_array_elements_text(targeted_countries) as country FROM pulses) as sub
    GROUP BY country ORDER BY count DESC LIMIT 5
""")
top_countries = cur.fetchall()

# Query 4: Top 5 tags
cur.execute("""
    SELECT tag, COUNT(*) as count
    FROM (SELECT jsonb_array_elements_text(tags) as tag FROM pulses) as sub
    GROUP BY tag ORDER BY count DESC LIMIT 5
""")
top_tags = cur.fetchall()

# Query 5: Expired vs active indicators
cur.execute("""
    SELECT
        SUM(CASE WHEN expiration < NOW() THEN 1 ELSE 0 END) as expired,
        SUM(CASE WHEN expiration >= NOW() OR expiration IS NULL THEN 1 ELSE 0 END) as active
    FROM indicators
""")
expired, active = cur.fetchone()
total = expired + active
percent_expired = (expired / total * 100) if total > 0 else 0
percent_active = (active / total * 100) if total > 0 else 0

# Query 6: Pulse with most indicators
cur.execute("""
    SELECT p.id, p.name, COUNT(i.id) as indicator_count
    FROM pulses p LEFT JOIN indicators i ON p.id = i.pulse_id
    GROUP BY p.id, p.name ORDER BY indicator_count DESC LIMIT 1
""")
top_pulse = cur.fetchone()

# Query 7: Sample pulses and indicators
cur.execute("""
    SELECT p.id, p.name, p.description, i.type, i.indicator
    FROM pulses p JOIN indicators i ON p.id = i.pulse_id
    LIMIT 3
""")
samples = cur.fetchall()

# Close database connection
cur.close()
conn.close()

# Format the prompt
prompt = f
"""
Analyze the following threat intelligence data from AlienVault OTX:

- Total pulses: {total_pulses}
- Total indicators: {total_indicators}
- Indicator types: {', '.join([f'{t[0]}: {t[1]}' for t in indicator_types])}
- Top 5 targeted countries: {', '.join([f'{c[0]}: {c[1]}' for c in top_countries])}
- Top 5 tags: {', '.join([f'{t[0]}: {t[1]}' for t in top_tags])}
- Indicators status: {percent_expired:.2f}% expired, {percent_active:.2f}% active
- Pulse with most indicators: '{top_pulse[1]}' ({top_pulse[2]} indicators)

Sample pulses and indicators:
{chr(10).join([f"Pulse: {s[1]}\nDescription: {s[2]}\nIndicator: {s[3]} - {s[4]}" for s in samples])}

Provide a summary and key insights based on this data.
"""

# Function to query Grok
def query_grok(prompt):
    url = "https://api.x.ai/v1/completions"  # Replace with actual xAI API endpoint
    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "grok-3",  # Adjust model name as needed
        "prompt": prompt,
        "max_tokens": 500,
        "temperature": 0.7
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()["choices"][0]["text"].strip()
    else:
        return f"Error from Grok API: {response.status_code} - {response.text}"

# Query Claude
def query_claude(prompt):
    response = anthropic.messages.create(
        model="claude-3-5-sonnet-20241022",  # Adjust model as needed
        max_tokens=500,
        temperature=0.7,
        messages=[
            {"role": "user", "content": f"{HUMAN_PROMPT}{prompt}{AI_PROMPT}"}
        ]
    )
    return response.content[0].text.strip()

# Get responses from both LLMs
print("=== Grok Response ===")
grok_response = query_grok(prompt)
print(grok_response)

print("\n=== Claude Response ===")
claude_response = query_claude(prompt)
print(claude_response)
