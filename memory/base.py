from abc import abstractmethod

from pydantic import BaseModel


class Memory(BaseModel):
    @abstractmethod
    def save(self, user_id: str, user_input: str, assistant_response: str):
        pass

    @abstractmethod
    def retrieve(self, query: str, user_id: str) -> list[dict]:
        pass
