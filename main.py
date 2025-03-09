# main.py
from src.extract import extract_otx_pulses
from src.transform import transform_pulses
from src.load import load_to_postgres

def run_pipeline():
    """Run the full ETL pipeline."""
    print("Starting ETL pipeline...")
    pulses = extract_otx_pulses()
    if not pulses:
        print("No pulses fetched. Exiting.")
        return
    pulses_df, indicators_df = transform_pulses(pulses)
    load_to_postgres(pulses_df, indicators_df)
    print("Pipeline complete!")

if __name__ == "__main__":
    run_pipeline()