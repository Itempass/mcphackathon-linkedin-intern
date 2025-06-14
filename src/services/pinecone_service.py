"""
Service to handle interactions with the Pinecone vector database.
"""
import os
import logging
from typing import List, Dict, Any
from pinecone import Pinecone, PineconeException

from .embedding_service import EmbeddingService

# Set up logging
logger = logging.getLogger(__name__)

class PineconeService:
    """A service for querying a Pinecone index."""

    def __init__(self):
        """Initializes the PineconeService."""
        self.api_key = os.getenv("PINECONE_API_KEY")
        self.index_name = os.getenv("PINECONE_INDEX_NAME")

        if not self.api_key or not self.index_name:
            raise ValueError("PINECONE_API_KEY and PINECONE_INDEX_NAME environment variables must be set.")

        try:
            pc = Pinecone(api_key=self.api_key)
            
            # Check if index exists, create if it doesn't
            existing_indexes = [index.name for index in pc.list_indexes()]
            if self.index_name not in existing_indexes:
                logger.info(f"[PineconeService] Index '{self.index_name}' not found. Creating new index...")
                pc.create_index(
                    name=self.index_name,
                    dimension=1536,  # OpenAI embedding dimension
                    metric='cosine',
                    spec={
                        'serverless': {
                            'cloud': 'aws',
                            'region': 'us-east-1'
                        }
                    }
                )
                logger.info(f"[PineconeService] Created new index '{self.index_name}'.")
            
            self.index = pc.Index(self.index_name)
            logger.info(f"[PineconeService] Initialized and connected to index '{self.index_name}'.")
            # Log index stats to confirm connection
            stats = self.index.describe_index_stats()
            logger.info(f"[PineconeService] Index stats: {stats}")

        except PineconeException as e:
            logger.error(f"[PineconeService] Failed to initialize Pinecone: {e}")
            raise RuntimeError(f"Could not connect to Pinecone index '{self.index_name}'.") from e
        
        self.embedding_service = EmbeddingService()

    def upsert_to_pinecone(self, user_id: str, message_id: str, msg_content: str, direction: str) -> None:
        """
        Upserts a message to the Pinecone index.

        Args:
            user_id: The ID of the user who sent/received the message.
            message_id: The unique ID of the message (used as vector ID).
            msg_content: The content of the message to be vectorized.
            direction: The direction of the message ("sent" or "received").

        Raises:
            ValueError: If any required parameters are missing or invalid.
            Exception: If the upsert operation fails.
        """
        # Validate inputs
        if not user_id:
            raise ValueError("user_id must be provided.")
        if not message_id:
            raise ValueError("message_id must be provided.")
        if not msg_content or not isinstance(msg_content, str):
            raise ValueError("msg_content must be a non-empty string.")
        if direction not in ["sent", "received"]:
            raise ValueError("direction must be either 'sent' or 'received'.")

        try:
            logger.debug(f"[PineconeService] Creating embedding for message '{message_id}' from user '{user_id}'.")
            
            # Create embedding for the message content
            embedding = self.embedding_service.create_embedding(msg_content)
            
            # Prepare metadata
            metadata = {
                "user_id": user_id,
                "message_id": message_id,
                "msg_content": msg_content,
                "direction": direction
            }
            
            # Prepare the vector for upsert
            vector_data = {
                "id": message_id,
                "values": embedding,
                "metadata": metadata
            }
            
            logger.debug(f"[PineconeService] Upserting vector for message '{message_id}' to index '{self.index_name}'.")
            
            # Upsert to Pinecone
            self.index.upsert(vectors=[vector_data])
            
            logger.info(f"[PineconeService] Successfully upserted message '{message_id}' for user '{user_id}' with direction '{direction}'.")
            
        except PineconeException as e:
            logger.error(f"[PineconeService] Pinecone error during upsert for message '{message_id}': {e}")
            raise Exception(f"Failed to upsert message to Pinecone: {e}") from e
        except Exception as e:
            logger.error(f"[PineconeService] Unexpected error during upsert for message '{message_id}': {e}")
            raise Exception(f"Failed to upsert message to Pinecone: {e}") from e

    def query_messages(self, user_id: str, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Queries the Pinecone index for a user's messages.

        Args:
            user_id: The id of the user to filter results for.
            query: The natural language query string.
            top_k: The number of top results to return.

        Returns:
            A list of matching messages from Pinecone.
        """

        if not user_id:
            raise ValueError("user_id must be provided for Pinecone query.")

        logger.debug(f"[PineconeService] Generating embedding for query: '{query[:50]}...'")
        query_vector = self.embedding_service.create_embedding(query)

        pinecone_filter = {'user_id': user_id}
        
        try:
            logger.debug(f"[PineconeService] Querying index for user '{user_id}' with top_k={top_k}.")
            results = self.index.query(
                vector=query_vector,
                top_k=top_k,
                filter=pinecone_filter,
                include_metadata=True
            )
            
            if not results or not results['matches']:
                logger.info(f"[PineconeService] No matches found for user '{user_id}'.")
                return []

            logger.info(f"[PineconeService] Found {len(results['matches'])} matches for user '{user_id}'.")
            
            # Format and return the results
            formatted_results = []
            for match in results['matches']:
                formatted_results.append({
                    "score": match['score'],
                    **match.get('metadata', {})
                })
            return formatted_results

        except PineconeException as e:
            logger.error(f"[PineconeService] Error querying Pinecone for user '{user_id}': {e}")
            raise Exception("Failed to query Pinecone.") from e 