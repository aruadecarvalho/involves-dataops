import json
import logging

from .pipeline import run

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    print(json.dumps(run(), indent=2))
