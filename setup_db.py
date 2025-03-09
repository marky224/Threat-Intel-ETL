# setup_db.py
# One-Time Configuration
# Create Database in Postgresql prior
import psycopg2
from src.config import DB_CONFIG

# SQL schema
SCHEMA = """
-- Drop existing tables if they exist (for a fresh start)
DROP TABLE IF EXISTS indicators CASCADE;
DROP TABLE IF EXISTS pulses CASCADE;

-- Create pulses table for top-level metadata
CREATE TABLE pulses (
    id VARCHAR(50) PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    author_name VARCHAR(100),
    public BOOLEAN,
    revision INTEGER,
    adversary VARCHAR(100),
    industries JSONB,
    tlp VARCHAR(10) CHECK (tlp IN ('white', 'green', 'amber', 'red')),
    tags JSONB,
    created TIMESTAMP,
    modified TIMESTAMP,
    "references" JSONB,  -- Quoted to escape the reserved keyword
    targeted_countries JSONB
);

-- Create indicators table for IoCs linked to pulses
CREATE TABLE indicators (
    id INTEGER PRIMARY KEY,
    pulse_id VARCHAR(50) REFERENCES pulses(id) ON DELETE CASCADE,
    indicator TEXT NOT NULL,
    type VARCHAR(50),
    title TEXT,
    description TEXT,
    access_reason TEXT,
    created TIMESTAMP,
    is_active BOOLEAN,
    access_type VARCHAR(20) CHECK (access_type IN ('public', 'private', 'redacted')),
    content TEXT,
    role TEXT,
    expiration TIMESTAMP,
    access_groups JSONB,
    observations INTEGER
);
"""

def setup_database():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(SCHEMA)
        conn.commit()
        print("Database schema created successfully!")
    except Exception as e:
        print(f"Error setting up database: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    setup_database()