from datetime import datetime

import factory  # type: ignore

from app.models import Quiz
from app.tests.factories.base_factory import BaseFactory
from app.tests.factories.user_factory import UserFactory


class QuizFactory(BaseFactory[Quiz]):
    id = factory.Sequence(lambda x: x)
    title = factory.Faker("sentence")
    description = factory.Faker("paragraph")
    created_at = factory.LazyFunction(datetime.now)
    updated_at = factory.LazyFunction(datetime.now)

    user = factory.SubFactory(UserFactory)

    class Meta:
        model = Quiz
        sqlalchemy_session_persistence = "commit"
