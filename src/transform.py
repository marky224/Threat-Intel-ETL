# src/transform.py
import pandas as pd
import json

def transform_pulses(pulses_data):
    """
    Transform OTX-like JSON data into DataFrames for pulses and indicators.
    Args:
        pulses_data (list): List of pulse dictionaries from the JSON 'results'.
    Returns:
        tuple: (pulses_df, indicators_df)
    """
    # Lists to hold data for each table
    pulses_list = []
    indicators_list = []

    # Process each pulse
    for pulse in pulses_data:
        # Pulse-level data
        pulse_data = {
            "id": pulse["id"],
            "name": pulse["name"],
            "description": pulse.get("description", ""),
            "author_name": pulse["author_name"],
            "public": bool(pulse["public"]),  # Convert int (0/1) to boolean
            "revision": pulse["revision"],
            "adversary": pulse.get("adversary", ""),
            "industries": json.dumps(pulse["industries"]),  # Convert array to JSON string
            "tlp": pulse.get("tlp", "white").lower(),  # Default to "white" if missing
            "tags": json.dumps(pulse["tags"]),
            "created": pulse["created"],
            "modified": pulse["modified"],
            "references": json.dumps(pulse["references"]),
            "targeted_countries": json.dumps(pulse["targeted_countries"])
        }
        pulses_list.append(pulse_data)

        # Indicators within the pulse
        for indicator in pulse["indicators"]:
            indicator_data = {
                "id": int(indicator["id"]),
                "pulse_id": pulse["id"],  # Link to parent pulse
                "indicator": indicator["indicator"],
                "type": indicator["type"],
                "title": indicator.get("title", ""),
                "description": indicator.get("description", ""),
                "access_reason": indicator.get("access_reason", ""),
                "created": indicator["created"],
                "is_active": bool(indicator["is_active"]),  # Convert int (0/1) or bool to boolean
                "access_type": indicator.get("access_type", "public"),  # Default to "public" if missing
                "content": indicator.get("content", ""),
                "role": indicator["role"] if indicator["role"] is not None else "",
                "expiration": indicator["expiration"],
                "access_groups": json.dumps(indicator.get("access_groups", [])),
                "observations": indicator.get("observations", 0)  # Default to 0 if missing
            }
            indicators_list.append(indicator_data)

    # Create DataFrames
    pulses_df = pd.DataFrame(pulses_list)
    indicators_df = pd.DataFrame(indicators_list)

    # Remove duplicates based on primary keys
    pulses_df.drop_duplicates(subset=["id"], inplace=True)
    indicators_df.drop_duplicates(subset=["id"], inplace=True)

    return pulses_df, indicators_df
