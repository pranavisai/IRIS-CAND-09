import logging
from pathlib import Path


# Configure the app logger so runtime output is available in both console and file.
def setup_logging():
    # Resolve the project root, regardless of where the app runs.
    project_root = Path(__file__).resolve().parent.parent
    log_dir = project_root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(
                log_dir / "runtime.log",
                encoding="utf-8",
            ),
        ],
        force=True,
    )