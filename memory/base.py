from abc import abstractmethod, ABC

class Memory(ABC):
    @abstractmethod
    async def save(self, user_id: str, user_input: str, assistant_response: str):
        pass

    @abstractmethod
    async def retrieve(self, query: str, user_id: str) -> list[dict]:
        pass
