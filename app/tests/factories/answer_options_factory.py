import factory  # type: ignore

from app.models import AnswerOption
from app.tests.factories.base_factory import BaseFactory
from app.tests.factories.question_factory import QuestionFactory


class AnswerOptionFactory(BaseFactory[AnswerOption]):
    id = factory.Sequence(lambda x: x)
    content = factory.Faker("sentence")
    is_correct = factory.Iterator([True, False])

    question = factory.SubFactory(QuestionFactory)

    class Meta:
        model = AnswerOption
        sqlalchemy_session_persistence = "commit"
