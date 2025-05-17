# src/load.py
import psycopg2
from src.config import DB_CONFIG

def load_to_postgres(pulses_df, indicators_df):
    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Load pulses
        for _, row in pulses_df.iterrows():
            cursor.execute("""
                INSERT INTO pulses (id, name, description, author_name, public, revision, adversary, industries, tlp, tags, created, modified, "references", targeted_countries)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    description = EXCLUDED.description,
                    author_name = EXCLUDED.author_name,
                    public = EXCLUDED.public,
                    revision = EXCLUDED.revision,
                    adversary = EXCLUDED.adversary,
                    industries = EXCLUDED.industries,
                    tlp = EXCLUDED.tlp,
                    tags = EXCLUDED.tags,
                    created = EXCLUDED.created,
                    modified = EXCLUDED.modified,
                    "references" = EXCLUDED."references",
                    targeted_countries = EXCLUDED.targeted_countries
            """, tuple(row))

        # Load indicators
        for _, row in indicators_df.iterrows():
            cursor.execute("""
                INSERT INTO indicators (id, pulse_id, indicator, type, title, description, access_reason, created, is_active, access_type, content, role, expiration, access_groups, observations)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    pulse_id = EXCLUDED.pulse_id,
                    indicator = EXCLUDED.indicator,
                    type = EXCLUDED.type,
                    title = EXCLUDED.title,
                    description = EXCLUDED.description,
                    access_reason = EXCLUDED.access_reason,
                    created = EXCLUDED.created,
                    is_active = EXCLUDED.is_active,
                    access_type = EXCLUDED.access_type,
                    content = EXCLUDED.content,
                    role = EXCLUDED.role,
                    expiration = EXCLUDED.expiration,
                    access_groups = EXCLUDED.access_groups,
                    observations = EXCLUDED.observations
            """, tuple(row))

        conn.commit()
        print("Data loaded into database successfully!")
    except Exception as e:
        print(f"Error loading data: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
