from typing import Any

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.db import connection, transaction


class Command(BaseCommand):
    help = "Flush database records for all models or a specific model"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--model",
            type=str,
            help="Specify the model name to flush records (case-sensitive, e.g., User)",
        )
        parser.add_argument(
            "--yes",
            action="store_true",
            help="Confirm flush without prompt",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """Handle the flushing of database records and reset IDs."""

        model_name = options.get("model")
        confirm = options.get("yes", False)

        if not confirm:
            prompt = "Are you sure you want to flush "
            prompt += f"the model '{model_name}'" if model_name else "all models"
            prompt += "? [y/n]: "
            user_input = input(prompt)
            if user_input.lower() not in ["y", "yes"]:
                self.stdout.write(self.style.WARNING("Operation cancelled."))
                return

        def reset_sequence(table_name: str) -> None:
            """Reset auto-increment ID sequence for supported databases."""
            with connection.cursor() as cursor:
                if connection.vendor == "postgresql":
                    cursor.execute(
                        f'ALTER SEQUENCE "{table_name}_id_seq" RESTART WITH 1;'
                    )
                elif connection.vendor == "sqlite":
                    cursor.execute(
                        f"DELETE FROM sqlite_sequence WHERE name='{table_name}';"
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"ID reset not implemented for {connection.vendor}."
                        )
                    )

        if model_name:
            # Find the model automatically across all apps
            model = None
            for m in apps.get_models():
                if m.__name__ == model_name:
                    model = m
                    break

            if not model:
                raise CommandError(
                    f'Model "{model_name}" not found in any installed app.'
                )

            table_name = model._meta.db_table
            with transaction.atomic():
                deleted_count, _ = model.objects.all().delete()
                reset_sequence(table_name)

            self.stdout.write(
                self.style.SUCCESS(
                    f'Flushed {deleted_count} records from model "{model_name}" and reset IDs.'
                )
            )

        else:
            # Flush all models
            total_deleted = 0
            with transaction.atomic():
                for model in apps.get_models():
                    table_name = model._meta.db_table
                    deleted_count, _ = model.objects.all().delete()
                    total_deleted += deleted_count
                    reset_sequence(table_name)

            self.stdout.write(
                self.style.SUCCESS(
                    f"Flushed {total_deleted} records from all models and reset IDs."
                )
            )
