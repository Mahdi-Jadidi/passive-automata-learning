"""Export pinned Review09 CI artifact tables."""
from review08_export import CONFIG, main

if __name__ == "__main__":
    main(CONFIG.with_name("review09-pipeline.json"))
