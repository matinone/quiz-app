from datetime import datetime

import factory  # type: ignore

from app.models import User
from app.tests.factories.base_factory import BaseFactory


class UserFactory(BaseFactory[User]):
    id = factory.Sequence(lambda x: x)
    username = factory.Faker("user_name")
    email = factory.LazyAttribute(lambda x: f"{x.username}@example.com")
    password_hash = factory.LazyAttribute(lambda x: hash(x.username))
    created_at = factory.LazyFunction(datetime.now)

    class Meta:
        model = User
        sqlalchemy_session_persistence = "commit"
