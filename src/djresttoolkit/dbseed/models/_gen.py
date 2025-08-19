from faker import Faker
from pydantic import Field as PydField


class Generator:
    @classmethod
    def create_faker(cls) -> Faker:
        return Faker()

Gen = Generator.create_faker()
Field = PydField