"""Run the pinned M4 sparse RAW pipeline."""
from review08_pipeline import CONFIG, main


if __name__ == "__main__":
    main(CONFIG.with_name("review09-pipeline.json"))
