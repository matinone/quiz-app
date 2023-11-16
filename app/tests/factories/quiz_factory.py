from datetime import datetime

import factory  # type: ignore

from app.models import Quiz
from app.tests.factories.base_factory import BaseFactory


class QuizFactory(BaseFactory[Quiz]):
    id = factory.Sequence(lambda x: f"{x}")
    title = factory.Faker("sentence")
    description = factory.Faker("paragraph")
    created_at = factory.LazyFunction(datetime.now)
    updated_at = factory.LazyFunction(datetime.now)

    class Meta:
        model = Quiz
        sqlalchemy_session_persistence = "commit"