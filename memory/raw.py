from typing import List, Dict

context: List[Dict] = []

def save_interaction(user_id: str, user_input: str, assistant_response: str):
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
        result = context.append(interaction)
        print(f"Memory saved successfully: {len(interaction)} memories added")
    except Exception as e:
        print(f"Error saving interaction: {e}")

def retrieve_context(query: str, user_id: str) -> List[Dict]:
    """Retrieve relevant context from Mem0"""
    return context