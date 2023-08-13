import csv
import json
import os

from django.core.management.base import (
    BaseCommand,
    CommandError,
)

from recipes.models import Ingredient


class Command(BaseCommand):

    help = 'Import database from files'

    INGREDIENT_FILE = 'ingredients'

    CSV_FORMAT = '.csv'
    JSON_FORMAT = '.json'

    def add_arguments(self, parser):
        parser.add_argument(
            "path",
            type=str,
            help='File path.'
        )

    def handle(self, *args, **kwargs) -> None:
        path = kwargs['path']
        cls = type(self)
        try:
            if not os.path.isfile(path):
                raise RuntimeError(f'File `{path}` not exist.')
            ext = os.path.splitext(path)[1].lower()
            if ext == cls.CSV_FORMAT:
                self.load_from_csv(path)
            elif ext == cls.JSON_FORMAT:
                self.load_from_json(path)
            else:
                raise RuntimeError('Unsupported file format.')
        except Exception as error:
            raise CommandError(f'error: {type(error)} = {error}')

    def load_from_csv(self, file_name) -> None:
        with open(file_name) as file:
            reader = csv.reader(file)
            ingredients = []
            for row in reader:
                ingredient = Ingredient(name=row[0], measurement_unit=row[1])
                ingredients.append(ingredient)
            Ingredient.objects.bulk_create(ingredients)

    def load_from_json(self, file_name) -> None:
        with open(file_name) as file:
            data = json.load(file)
        ingredients = [Ingredient(**item) for item in data]
        Ingredient.objects.bulk_create(ingredients)
