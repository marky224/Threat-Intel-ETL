import requests
from anthropic import Anthropic
from datetime import datetime
from src.config import GROK_API_KEY, CLAUDE_API_KEY
from src.sql_queries import run_all_queries

def run_llm_pipeline():
    print("Generating LLM Response Results")
    # Run SQL queries
    query_results = run_all_queries()

    # Check for database connection error
    if "error" in query_results:
        print(f"Database error: {query_results['error']}")
        exit(1)

    # Extract results
    total_pulses = query_results["total_pulses"][0][0]
    total_indicators = query_results["total_indicators"][0][0]
    indicator_types = query_results["indicator_types"]
    top_countries = query_results["top_countries"]
    top_tags = query_results["top_tags"]
    expired, active = query_results["expired_active"][0]
    top_pulse = query_results["top_pulse"][0]
    pulse_trends = query_results["pulse_trends"]
    tlp_indicators = query_results["tlp_indicators"]
    multi_type_pulses = query_results["multi_type_pulses"]
    expiring_indicators = query_results["expiring_indicators"]
    top_industries = query_results["top_industries"]

    # Calculate expired/active percentages
    total = expired + active
    percent_expired = (expired / total * 100) if total > 0 else 0
    percent_active = (active / total * 100) if total > 0 else 0

    # Format the prompt
    prompt = f"""
    Analyze the following threat intelligence data from AlienVault OTX, collected on {datetime.now().strftime('%Y-%m-%d')}:

    - Total pulses: {total_pulses}
    - Total indicators: {total_indicators}
    - Top 5 indicator types: {', '.join([f'{t[0]}: {t[1]}' for t in indicator_types])}
    - Top 5 targeted countries: {', '.join([f'{c[0]}: {c[1]}' for c in top_countries])}
    - Top 5 tags: {', '.join([f'{t[0]}: {t[1]}' for t in top_tags])}
    - Indicators status: {percent_expired:.2f}% expired, {percent_active:.2f}% active
    - Pulse with most indicators: '{top_pulse[1]}' ({top_pulse[2]} indicators)
    - Temporal trends (last 6 months): {', '.join(['{}: {} pulses'.format(t[0].strftime('%Y-%m'), t[1]) for t in pulse_trends])}
    - Top 5 TLP indicators: {', '.join([f'TLP {t[0]} - {t[1]}: {t[2]}' for t in tlp_indicators])}
    - Top 3 pulses with multiple indicator types: {', '.join(["'{}': {} types".format(p[1], p[2]) for p in multi_type_pulses])}
    - Indicators expiring soon: {', '.join(['{}: {} (expires {})'.format(i[0], i[1], i[2].strftime('%Y-%m-%d %H:%M:%S')) for i in expiring_indicators])}
    - Top 5 targeted industries: {', '.join([f'{i[0]}: {i[1]} pulses' for i in top_industries])}

    Provide a concise summary and 3-5 key insights, focusing on the most critical threats and trends.
    """

    # Function to query Grok
    def query_grok(prompt):
        url = "https://api.x.ai/v1/completions"  # Adjust if endpoint changes
        headers = {
            "Authorization": f"Bearer {GROK_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "grok-3",
            "prompt": prompt,
            "max_tokens": 500,
            "temperature": 0.7
        }
        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            return response.json()["choices"][0]["text"].strip()
        except Exception as e:
            return f"Error from Grok API: {e}"

    # Function to query Claude
    def query_claude(prompt):
        # Initialize Anthropic client for Claude
        anthropic = Anthropic(api_key=CLAUDE_API_KEY)
        try:
            response = anthropic.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip()
        except Exception as e:
            return f"Error from Claude API: {e}"

    # Get and print responses
    print("=== Grok Response ===")
    grok_response = query_grok(prompt)
    print(grok_response)

    print("\n=== Claude Response ===")
    claude_response = query_claude(prompt)
    print(claude_response)

if __name__ == "__main__":
    run_llm_pipeline()
