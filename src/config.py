import logging
from pathlib import Path

# Настройки приложения
BASE_DIR = Path(__file__).parent.parent.parent
DB_PATH = BASE_DIR / "urls.db"
LOG_PATH = BASE_DIR / "app.log"

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)