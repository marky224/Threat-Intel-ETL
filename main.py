# main.py
from src.extract import extract_otx_pulses
from src.transform import transform_pulses
from src.load import load_to_postgres
from src.send_to_llms import run_llm_pipeline
import sys
from contextlib import contextmanager

@contextmanager
def tee(file_path):
    """Redirect stdout to both console and a file."""
    original_stdout = sys.stdout
    with open(file_path, 'w') as f:
        class Tee:
            def write(self, data):
                f.write(data)
                f.flush()
                original_stdout.write(data)
                original_stdout.flush()
            def flush(self):
                f.flush()
                original_stdout.flush()
        sys.stdout = Tee()
        try:
            yield
        finally:
            sys.stdout = original_stdout

def run_pipeline():
    """Run the full ETL pipeline."""
    print("Starting ETL pipeline...")
    pulses = extract_otx_pulses()
    if not pulses:
        print("No pulses fetched. Exiting.")
        return
    pulses_df, indicators_df = transform_pulses(pulses)
    load_to_postgres(pulses_df, indicators_df)
    run_llm_pipeline()
    print("Pipeline complete!")

if __name__ == "__main__":
    with tee('pipeline_output.txt'):
        run_pipeline()
