from typing import List, Dict

from memory.base import Memory

class RawMemory(Memory):
    context: List[List[Dict]] = []
    
    def __init__(self):
        super().__init__(context=[])

    def save(self, user_id: str, user_input: str, assistant_response: str):
        """Save the interaction to Mem0"""
        try:
            interaction = [
                {
                "role": "user",
                "content": user_input
                },
                {
                    "role": "assistant",
                    "content": assistant_response
                }
            ]
            result = self.context.append(interaction)
            print(f"Memory saved successfully: {len(interaction)} memories added")
        except Exception as e:
            print(f"Error saving interaction: {e}")

    def retrieve(self, query: str, user_id: str) -> List[Dict]:
        """Retrieve relevant context from Mem0"""
        return self.context