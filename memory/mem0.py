
from dotenv import load_dotenv
from mem0 import MemoryClient

from memory.base import Memory


load_dotenv()

mem0 = MemoryClient()

class Mem0Memory(Memory):
    def retrieve(self, query: str, user_id: str) -> list[dict]:
        """Retrieve relevant context from Mem0."""
        try:
            memories = mem0.search(query=query, user_id=user_id, filters={'user_id': user_id})
            memory_list = memories['results']

            serialized_memories = ' '.join([mem['memory'] for mem in memory_list])
            return [
                {
                    'role': 'system',
                    'content': f'Relevant information: {serialized_memories}'
                },
                {
                    'role': 'user',
                    'content': query
                }
            ]
        except Exception as e:
            print(f'Error retrieving memories: {e}')
            # Return empty context if there's an error
            return [{'role': 'user', 'content': query}]

    def save(self, user_id: str, user_input: str, assistant_response: str) -> None:
        """Save the interaction to Mem0."""
        try:
            interaction = [
                {
                'role': 'user',
                'content': user_input
                },
                {
                    'role': 'assistant',
                    'content': assistant_response
                }
            ]
            result = mem0.add(interaction, user_id=user_id)
            print(f"Memory saved successfully: {len(result.get('results', []))} memories added")
        except Exception as e:
            print(f'Error saving interaction: {e}')
