import asyncio

from utils.chat_adapter import chat_loop

if __name__ == '__main__':
    asyncio.run(chat_loop(user_id='albert', session_id='123'))
