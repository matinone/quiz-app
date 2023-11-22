import random
from datetime import datetime

import factory  # type: ignore

from app.models import Question
from app.schemas import QuestionType
from app.tests.factories.base_factory import BaseFactory
from app.tests.factories.quiz_factory import QuizFactory


class QuestionFactory(BaseFactory[Question]):
    id = factory.Sequence(lambda x: x)
    content = factory.Faker("sentence")
    type = factory.Iterator([e.value for e in QuestionType])
    points = factory.LazyAttribute(lambda x: random.randint(0, 10))
    created_at = factory.LazyFunction(datetime.now)
    updated_at = factory.LazyFunction(datetime.now)

    quiz = factory.SubFactory(QuizFactory)

    class Meta:
        model = Question
        sqlalchemy_session_persistence = "commit"
