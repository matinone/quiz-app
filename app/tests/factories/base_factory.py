from typing import Generic, TypeVar

from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory  # type: ignore

T = TypeVar("T")


# see https://github.com/FactoryBoy/factory_boy/issues/468
class BaseFactory(Generic[T], AsyncSQLAlchemyFactory):
    @classmethod
    async def create(cls, **kwargs) -> T:
        return await super().create(**kwargs)

    @classmethod
    async def create_batch(cls, *args, **kwargs) -> list[T]:
        return await super().create_batch(*args, **kwargs)
