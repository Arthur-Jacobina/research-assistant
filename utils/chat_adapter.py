from llm.agent import workflow
# from memory.mem0 import Mem0Memory
from memory.raw import RawMemory

# TODO: Implement a batch flush and insertion triggered by mem0 webhook
# memory = Mem0Memory(
memory = RawMemory()

async def chat_interaction(user_input: str, user_id: str, session_id: str) -> str:
    context = await memory.retrieve(user_input, user_id)

    agent = workflow(user_input=user_input)
    
    response = agent(user_input=user_input, context=context)

    await memory.save(user_id, user_input, response.response)

    return response.response

async def chat_loop(user_id:  str, session_id: str) -> None:
    print('Welcome to your personal Research Agent! How can I assist you with your research today?')
    while True:
        user_input = input('You: ')
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print('Research Agent: Thank you for using our research service. Have a great research!')
            break
        response = await chat_interaction(user_input, user_id, session_id)
        print(f'Research Agent: {response}')
