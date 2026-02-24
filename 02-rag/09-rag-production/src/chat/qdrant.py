from qdrant_client import QdrantClient, AsyncQdrantClient

from src.customlogger import setup_logger
from src.settings import settings

logger = setup_logger(__name__)

client = QdrantClient(
    host=settings.QDRANT_HOST,
    port=settings.QDRANT_PORT,
    timeout=120,
)

aclient = AsyncQdrantClient(
    host=settings.QDRANT_HOST,
    port=settings.QDRANT_PORT,
    timeout=120,
)