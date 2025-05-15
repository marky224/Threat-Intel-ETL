# src/extract.py
from OTXv2 import OTXv2
from src.config import OTX_API_KEY

def extract_otx_pulses():
    print("Fetching OTX pulses...")
    try:
        otx = OTXv2(OTX_API_KEY)
        # Get all subscribed pulses
        pulses = otx.getall()  # Fetches all pulses you’re subscribed to
        if not pulses:
            print("No pulses fetched. Check subscriptions or API key.")
            return []
        print(f"Fetched {len(pulses)} pulses.")
        return pulses
    except Exception as e:
        print(f"Error fetching OTX data: {e}")
        return []
