import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient

# Load environment variables once
load_dotenv()

def getQdrantClient(prefer_grpc: bool = False, verify_ssl: bool = False) -> QdrantClient:
    """
    Returns a connected QdrantClient instance.

    Args:
        prefer_grpc (bool): Whether to use gRPC or HTTP. Default: False (HTTP)
        verify_ssl (bool): Whether to verify SSL certificates. Default: False
                           Set True if SSL certs are properly configured.
    Returns:
        QdrantClient: Connected client instance
    """
    QDRANT_URL = os.getenv("QDRANT_URL")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

    if not QDRANT_URL or not QDRANT_API_KEY:
        raise ValueError("QDRANT_URL or QDRANT_API_KEY not set in .env")

    client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        prefer_grpc=False, 
        https=True,
        verify=verify_ssl # Use verify=True if your SSL setup works fine
    )
    return client

