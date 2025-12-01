
from memory.base import Memory


class RawMemory(Memory):
    context: list[list[dict]] = []

    def __init__(self) -> None:
        super().__init__(context=[])

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
            self.context.append(interaction)
            print(f'Memory saved successfully: {len(interaction)} memories added')
        except Exception as e:
            print(f'Error saving interaction: {e}')

    def retrieve(self, query: str, user_id: str) -> list[dict]:
        """Retrieve relevant context from Mem0."""
        return self.context
