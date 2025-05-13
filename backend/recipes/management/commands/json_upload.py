import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Import data from JSON file into Ingredient model in database'

    def handle(self, *args, **kwargs):
        file_path = f'{settings.BASE_DIR}/data/ingredients.json'
        if not os.path.exists(file_path):
            self.stderr.write(
                self.style.ERROR(f'Fild with root {file_path} not found.')
            )
            return

        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            for item in data:
                ingredient, created = Ingredient.objects.get_or_create(
                    name=item['name'],
                    measurement_unit=item['measurement_unit']
                )
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Ingredient {ingredient.name} added.'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Ingredient {ingredient.name} already exist.'
                        )
                    )
