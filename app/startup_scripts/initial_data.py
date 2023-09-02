import logging

from app.database.init_db import init_db
from app.database.session import SessionLocal
from app.utils.api_logger import logzz

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init() -> None:
    db = SessionLocal()
    init_db(db)


def main() -> None:
    logger.info("Creating initial data.")
    init()
    logger.info("Initial data created.")
    logzz.info("First super user created @:", timestamp=True)

if __name__ == "__main__":
    main()
