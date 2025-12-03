from braintrust import current_span, traced
import asyncio

# This mechanism is not so reliable. Autoscaling would kill it
# And its not context efficient but for small stuff it's fine
local_memory = {}

class RawMemory():

    @traced(name="Memory Retrieval")
    async def retrieve(self, query: str, user_id: str) -> list[dict]:
        """Retrieve relevant context from Mem0"""
        return local_memory.get(user_id, [])[:10]

    @traced(name="Memory Saving")
    async def save(self, user_id: str, user_input: str, assistant_response: str):
        """Save the interaction to Mem0"""
        if user_id not in local_memory:
            local_memory[user_id] = []
        local_memory[user_id].append({
            "user_input": user_input,
            "assistant_response": assistant_response[:800]
        })