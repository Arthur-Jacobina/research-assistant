import os
import traceback

from braintrust import current_span, traced
from dotenv import load_dotenv
from mem0 import AsyncMemoryClient

from memory.base import Memory


load_dotenv()

mem0 = AsyncMemoryClient(api_key=os.getenv('MEM0_API_KEY'))


class Mem0Memory(Memory):
    """Mem0 memory implementation."""

    @traced(name="Memory Retrieval")
    async def retrieve(self, query: str, user_id: str) -> list[dict]:
        """Retrieve relevant context from Mem0."""
        try:
            result = await mem0.search(query=query, filters={'user_id': user_id})
            # Handle both v1.1 format (dict with 'results') and legacy format (list)
            memories = result.get('results', result) if isinstance(result, dict) else result
            serialized_memories = ' '.join([mem['memory'] for mem in memories])
            context = [
                {
                    'role': 'system',
                    'content': f'Relevant information: {serialized_memories}',
                },
                {'role': 'user', 'content': query},
            ]
            current_span().log(
                metadata={
                    'memory_retrieved': context,
                    'query': query,
                    'user_id': user_id,
                }
            )
        except Exception as e:
            current_span().log(
                error = f'Error retrieving memory: {e!s} \n {traceback.format_exc()}'
            )
            return [{'role': 'user', 'content': query}]
        else:
            return context

    @traced(name="Memory Saving")
    async def save(
        self, user_id: str, user_input: str, assistant_response: str
    ) -> None:
        """Save the interaction to Mem0."""
        try:
            interaction = [
                {'role': 'user', 'content': user_input},
                {'role': 'assistant', 'content': assistant_response},
            ]
            result = await mem0.add(interaction, user_id=user_id)
            current_span().log(
                metadata={'memory_saved': result, 'user_id': user_id}
            )
        except Exception as e:
            current_span().log(
                error = f'Error saving memory: {e!s} \n {traceback.format_exc()}'
            )
