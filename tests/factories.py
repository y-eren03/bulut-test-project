import factory
from src.models import Task, Tag
from faker import Faker

fake = Faker()


class TaskFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Task
        sqlalchemy_session_persistence = "commit"

    title = factory.Faker("sentence", nb_words=4)
    description = factory.Faker("paragraph")
    is_completed = factory.Faker("boolean", chance_of_getting_true=20)
    attachment_url = factory.LazyAttribute(
        lambda o: f"http://localhost:4566/todo-attachments/{fake.file_name(extension='pdf')}"
        if fake.boolean()
        else None
    )


class TagFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Tag
        sqlalchemy_session_persistence = "commit"

    name = factory.Faker("word")
    task = factory.SubFactory(TaskFactory)
