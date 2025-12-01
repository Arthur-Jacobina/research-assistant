from agent.core import ag
from memory.raw import RawMemory


memory = RawMemory()

def chat_interaction(user_input: str, user_id: str, session_id: str) -> str:
    context = memory.retrieve(user_input, user_id)

    response = ag(user_input=user_input, context=context)

    memory.save(user_id, user_input, response.response)

    return response.response

def chat_loop(user_id: str, session_id: str) -> None:
    print('Welcome to your personal Research Agent! How can I assist you with your research today?')
    while True:
        user_input = input('You: ')
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print('Research Agent: Thank you for using our research service. Have a great research!')
            break
        response = chat_interaction(user_input, user_id, session_id)
        print(f'Research Agent: {response}')
