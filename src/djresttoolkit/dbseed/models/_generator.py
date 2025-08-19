from faker import Faker


class Generator:
    @classmethod
    def create_faker(cls) -> Faker:
        return Faker()

generator = Generator.create_faker()
