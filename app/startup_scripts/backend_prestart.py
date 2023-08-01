import logging

from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed
from app.database.session import SessionLocal
from app.utils.logger import logzz

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
def init() -> None:
    try:
        db = SessionLocal()
        # Try to create session to check if DB is awake
        db.execute("SELECT 1")
    except Exception as e:
        logger.error(e)
        logzz.error(f'{str(e)}', timestamp=1)
        raise e


def main() -> None:
    logger.info("Initializing database service")
    init()
    logger.info("Service is awake.")
    logzz.info('Database awake and purring...')

if __name__ == "__main__":
    main()