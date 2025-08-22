import pkgutil
from importlib import import_module
from types import ModuleType
from typing import Any

from django.apps import apps
from django.core.management.base import BaseCommand, CommandParser
from django.db import transaction
from django.db.models import Model, QuerySet

from djresttoolkit.dbseed.models import SeedModel


class Command(BaseCommand):
    help = "Seed the database with fake data for any Django model"

    def add_arguments(self, parser: CommandParser) -> None:
        """Add command arguments."""
        parser.add_argument(
            "--count",
            type=int,
            default=5,
            help="Number of records per model",
        )
        parser.add_argument(
            "--model",
            type=str,
            default=None,
            help="Specific model name to seed (e.g., User, Product)",
        )
        parser.add_argument(
            "--seed",
            type=int,
            default=None,
            help="Optional Faker seed for reproducible data",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """Handle ForeignKey, OneToOneField and ManyToMany relationship."""

        count = options["count"]
        model_name = options["model"]
        seed = options["seed"]

        if seed is not None:
            from faker import Faker

            faker = Faker()
            faker.seed_instance(seed)

        seed_model_classes: list[type[SeedModel]] = []

        # Discover all dbseed dirs in installed apps
        for app_config in apps.get_app_configs():
            try:
                module: ModuleType = import_module(f"{app_config.name}.dbseed")
            except ModuleNotFoundError:
                continue  # app has no dbseed dir

            # Iterate over modules in the dbseed package
            for _, name, ispkg in pkgutil.iter_modules(module.__path__):
                if ispkg:
                    continue

                submodule = import_module(f"{app_config.name}.dbseed.{name}")
                for attr_name in dir(submodule):
                    attr = getattr(submodule, attr_name)
                    if (
                        isinstance(attr, type)
                        and issubclass(attr, SeedModel)
                        and attr is not SeedModel
                    ):
                        # Filter by model name if provided
                        if (
                            not model_name
                            or model_name.lower()
                            == attr.__name__.replace("SeedModel", "").lower()
                        ):
                            seed_model_classes.append(attr)

        if not seed_model_classes:
            self.stdout.write(self.style.WARNING("No matching dbseed models found."))
            return None

        # Generate fake data for each discovered dbseed model
        for dbseed_cls in seed_model_classes:
            django_model = dbseed_cls.get_model()
            created_count: int = 0

            for _ in range(count):
                try:
                    with transaction.atomic():
                        data, m2m_fields = dbseed_cls.create_instance()
                        obj = django_model.objects.create(**data)
                        created_count += 1

                        # Assign ManyToMany fields
                        for m2m_field in m2m_fields:
                            rel_model = m2m_field.remote_field.model
                            related_instances: QuerySet[Model] | list[Any] = (
                                rel_model.objects.order_by("?")[:2]
                                if rel_model.objects.exists()
                                else []
                            )
                            getattr(obj, m2m_field.name).set(related_instances)
                except Exception as error:
                    self.stderr.write(
                        f"Error creating {django_model.__name__} instance: {error}"
                    )
                    continue
            self.stdout.write(
                self.style.SUCCESS(
                    f"{created_count} records inserted for {django_model.__name__}"
                )
            )
