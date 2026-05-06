from abc import ABC,abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.generatorService import OpenAIService

class BaseGeneratorRepository(ABC):
    def __init__(self,db:AsyncSession):
        self.db = db

    @abstractmethod
    async def get_response_from_generatorservice(self,airesponse:str):
        pass
    @abstractmethod
    async def update_response_todb(self,responce:str):
        pass

class GeneratorRepository(BaseGeneratorRepository):
    def __init__(self,db:AsyncSession):
        super().__init__(db)

    async def get_response_from_generatorservice(self,airesponse:str):
        pass


