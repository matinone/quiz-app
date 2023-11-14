from typing import Generic, TypeVar

from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory  # type: ignore

T = TypeVar("T")


# see https://github.com/FactoryBoy/factory_boy/issues/468
class BaseFactory(Generic[T], AsyncSQLAlchemyFactory):
    @classmethod
    def create(cls, **kwargs) -> T:
        return super().create(**kwargs)
