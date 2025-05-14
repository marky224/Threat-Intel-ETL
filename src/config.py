# src/config.py

# AlienVault OTX API Key for fetching threat intelligence
OTX_API_KEY = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"  # Updates to Credentials for OTI DirectConnect API

# xAI API key for accessing Grok
GROK_API_KEY = "your-xai-api-key" # Updates to Credentials for Grok API

# Anthropic API key for accessing Claude
CLAUDE_API_KEY = "your-anthropic-api-key" # Updates to Credentials for Claude API

# PostgreSQL Database Configuration
DB_CONFIG = {                                                                      # Credentials for PostgreSQL Database
    "dbname": "threat_intel",
    "user": "XXXXXXXXX",           # Update
    "password": "XXXXXXXXXX",      # Update
    "host": "localhost",
    "port": "5432"
}
