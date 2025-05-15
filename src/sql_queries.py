import psycopg2
from src.config import DB_CONFIG

def run_query(cursor, query, query_name):
    """Execute a query and print its results, handling errors."""
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        print(f"\n=== {query_name} ===")
        if results:
            for row in results:
                print(row)
        else:
            print("No results returned.")
        return results
    except Exception as e:
        print(f"Error in {query_name}: {e}")
        return None

# Connect to the database
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    print("Connected to database successfully.")
except Exception as e:
    print(f"Failed to connect to database: {e}")
    exit(1)

# Existing Queries (from send_to_llms.py)
queries = [
    {
        "name": "Total Pulses",
        "query": "SELECT COUNT(*) FROM pulses"
    },
    {
        "name": "Total Indicators",
        "query": "SELECT COUNT(*) FROM indicators"
    },
    {
        "name": "Indicator Type Distribution",
        "query": "SELECT type, COUNT(*) as count FROM indicators GROUP BY type ORDER BY count DESC"
    },
    {
        "name": "Top 5 Targeted Countries",
        "query": """
            SELECT country, COUNT(*) as count
            FROM (SELECT jsonb_array_elements_text(targeted_countries) as country FROM pulses) as sub
            GROUP BY country ORDER BY count DESC LIMIT 5
        """
    },
    {
        "name": "Top 5 Tags",
        "query": """
            SELECT tag, COUNT(*) as count
            FROM (SELECT jsonb_array_elements_text(tags) as tag FROM pulses) as sub
            GROUP BY tag ORDER BY count DESC LIMIT 5
        """
    },
    {
        "name": "Expired vs Active Indicators",
        "query": """
            SELECT
                SUM(CASE WHEN expiration < NOW() THEN 1 ELSE 0 END) as expired,
                SUM(CASE WHEN expiration >= NOW() OR expiration IS NULL THEN 1 ELSE 0 END) as active
            FROM indicators
        """
    },
    {
        "name": "Pulse with Most Indicators",
        "query": """
            SELECT p.id, p.name, COUNT(i.id) as indicator_count
            FROM pulses p LEFT JOIN indicators i ON p.id = i.pulse_id
            GROUP BY p.id, p.name ORDER BY indicator_count DESC LIMIT 1
        """
    },
    {
        "name": "Sample Pulses and Indicators",
        "query": """
            SELECT p.id, p.name, p.description, i.type, i.indicator
            FROM pulses p JOIN indicators i ON p.id = i.pulse_id
            LIMIT 3
        """
    },
    # New Queries
    {
        "name": "Temporal Trend of Pulses (Last 6 Months)",
        "query": """
            SELECT DATE_TRUNC('month', created) AS month, COUNT(*) AS pulse_count
            FROM pulses
            GROUP BY DATE_TRUNC('month', created)
            ORDER BY month DESC
            LIMIT 6
        """
    },
    {
        "name": "High-Risk Indicators by TLP",
        "query": """
            SELECT p.tlp, i.type, COUNT(i.id) AS indicator_count
            FROM pulses p
            JOIN indicators i ON p.id = i.pulse_id
            WHERE p.tlp IN ('red', 'amber', 'green', 'white')
            GROUP BY p.tlp, i.type
            ORDER BY p.tlp, indicator_count DESC
        """
    },
    {
        "name": "Pulses with Multiple Indicator Types",
        "query": """
            SELECT p.id, p.name, COUNT(DISTINCT i.type) AS type_count
            FROM pulses p
            JOIN indicators i ON p.id = i.pulse_id
            GROUP BY p.id, p.name
            HAVING COUNT(DISTINCT i.type) > 1
            ORDER BY type_count DESC
            LIMIT 5
        """
    },
    {
        "name": "Indicators Expiring Soon",
        "query": """
            SELECT i.type, i.indicator, i.expiration
            FROM indicators i
            WHERE i.expiration IS NOT NULL
              AND i.expiration BETWEEN NOW() AND NOW() + INTERVAL '30 days'
            ORDER BY i.expiration
            LIMIT 10
        """
    },
    {
        "name": "Top Industries Targeted",
        "query": """
            SELECT industry, COUNT(*) AS pulse_count
            FROM (SELECT jsonb_array_elements_text(industries) AS industry FROM pulses) AS sub
            GROUP BY industry
            ORDER BY pulse_count DESC
            LIMIT 5
        """
    }
]

# Run all queries
for q in queries:
    run_query(cur, q["query"], q["name"])

# Close connection
cur.close()
conn.close()
print("\nAll queries executed. Connection closed.")
