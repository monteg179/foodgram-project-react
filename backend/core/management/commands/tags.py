import csv
import json
import os

from django.core.management.base import (
    BaseCommand,
    CommandError,
)

from recipes.models import Tag


class Command(BaseCommand):

    help = 'Import tags data from files'

    INGREDIENT_FILE = 'tags'

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
            tags = []
            for row in reader:
                tag = Tag(name=row[0], color=row[1], slug=row[2])
                tags.append(tag)
            Tag.objects.bulk_create(tags)

    def load_from_json(self, file_name) -> None:
        with open(file_name) as file:
            data = json.load(file)
        tags = [Tag(**item) for item in data]
        Tag.objects.bulk_create(tags)
