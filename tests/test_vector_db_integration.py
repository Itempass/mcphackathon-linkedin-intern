import pytest
import uuid
from api.services import qdrant_client
from api.services.embedding_service import EmbeddingService
from qdrant_client import models

@pytest.mark.asyncio
async def test_qdrant_integration():
    """
    An integration test that hits a running Qdrant instance.
    """
    user_id = f"test-user-{uuid.uuid4()}"
    message_id = f"test-message-{uuid.uuid4()}"
    message_content = "This is a test message for integration testing."

    try:
        # 1. Upsert a message, which will also test the embedding service
        qdrant_client.upsert_message(
            user_id=user_id,
            message_id=message_id,
            msg_content=message_content,
            direction="sent",
        )

        # 2. Perform a semantic search to find the message
        search_results = qdrant_client.semantic_search(
            collection_name="emails",
            query=message_content,
            user_id=user_id,
            top_k=1,
        )

        # 3. Assert that the message was found
        assert len(search_results) > 0
        assert search_results[0]["message_id"] == message_id
        assert search_results[0]["msg_content"] == message_content

    finally:
        # 4. Clean up by deleting the test point
        qdrant_client.qdrant_client.delete_points(
            collection_name="emails",
            points_selector=models.PointIdsList(points=[message_id]),
        ) 