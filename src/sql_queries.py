import psycopg2
from src.config import DB_CONFIG

def run_all_queries():
    """
    Execute all SQL queries against the threat_intel database and return results.
    Returns a dictionary with query names as keys and result lists as values.
    """
    results = {}
    
    # Connect to the database
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
    except Exception as e:
        return {"error": f"Failed to connect to database: {e}"}

    queries = [
        {
            "name": "total_pulses",
            "query": "SELECT COUNT(*) FROM pulses"
        },
        {
            "name": "total_indicators",
            "query": "SELECT COUNT(*) FROM indicators"
        },
        {
            "name": "indicator_types",
            "query": "SELECT type, COUNT(*) as count FROM indicators GROUP BY type ORDER BY count DESC LIMIT 5"
        },
        {
            "name": "top_countries",
            "query": """
                SELECT country, COUNT(*) as count
                FROM (SELECT jsonb_array_elements_text(targeted_countries) as country FROM pulses) as sub
                GROUP BY country ORDER BY count DESC LIMIT 5
            """
        },
        {
            "name": "top_tags",
            "query": """
                SELECT tag, COUNT(*) as count
                FROM (SELECT jsonb_array_elements_text(tags) as tag FROM pulses) as sub
                GROUP BY tag ORDER BY count DESC LIMIT 5
            """
        },
        {
            "name": "expired_active",
            "query": """
                SELECT
                    SUM(CASE WHEN expiration < NOW() THEN 1 ELSE 0 END) as expired,
                    SUM(CASE WHEN expiration >= NOW() OR expiration IS NULL THEN 1 ELSE 0 END) as active
                FROM indicators
            """
        },
        {
            "name": "top_pulse",
            "query": """
                SELECT p.id, p.name, COUNT(i.id) as indicator_count
                FROM pulses p LEFT JOIN indicators i ON p.id = i.pulse_id
                GROUP BY p.id, p.name ORDER BY indicator_count DESC LIMIT 1
            """
        },
        {
            "name": "samples",
            "query": """
                SELECT p.id, p.name, p.description, i.type, i.indicator
                FROM pulses p JOIN indicators i ON p.id = i.pulse_id
                LIMIT 3
            """
        },
        {
            "name": "pulse_trends",
            "query": """
                SELECT DATE_TRUNC('month', created) AS month, COUNT(*) AS pulse_count
                FROM pulses
                GROUP BY DATE_TRUNC('month', created)
                ORDER BY month DESC
                LIMIT 6
            """
        },
        {
            "name": "tlp_indicators",
            "query": """
                SELECT p.tlp, i.type, COUNT(i.id) AS indicator_count
                FROM pulses p
                JOIN indicators i ON p.id = i.pulse_id
                WHERE p.tlp IN ('red', 'amber', 'green', 'white')
                GROUP BY p.tlp, i.type
                ORDER BY indicator_count DESC
                LIMIT 5
            """
        },
        {
            "name": "multi_type_pulses",
            "query": """
                SELECT p.id, p.name, COUNT(DISTINCT i.type) AS type_count
                FROM pulses p
                JOIN indicators i ON p.id = i.pulse_id
                GROUP BY p.id, p.name
                HAVING COUNT(DISTINCT i.type) > 1
                ORDER BY type_count DESC
                LIMIT 3
            """
        },
        {
            "name": "expiring_indicators",
            "query": """
                SELECT i.type, i.indicator, i.expiration
                FROM indicators i
                WHERE i.expiration IS NOT NULL
                  AND i.expiration BETWEEN NOW() AND NOW() + INTERVAL '30 days'
                ORDER BY i.expiration
                LIMIT 5
            """
        },
        {
            "name": "top_industries",
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
        try:
            cur.execute(q["query"])
            results[q["name"]] = cur.fetchall()
        except Exception as e:
            results[q["name"]] = {"error": f"Query failed: {e}"}

    # Close connection
    cur.close()
    conn.close()
    return results
