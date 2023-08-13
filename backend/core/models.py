import csv
import json
from typing import Any, Collection
from django.db.models import Model
from django.db.models.query import QuerySet
CSV_FORMAT = 'csv'
JSON_FORMAT = 'json'
FORMAT_ENUM = (CSV_FORMAT, JSON_FORMAT)


class FoodgramModelMixin:

    @classmethod
    def clear_data(cls) -> None:
        cls.objects.all().delete()

    @classmethod
    def import_data(cls, data: dict[str, Any]) -> Model:
        raise NotImplementedError()

    @classmethod
    def export_fieldnames(cls) -> Collection[str]:
        raise NotImplementedError()

    @classmethod
    def export_queryset(cls) -> QuerySet:
        return cls.objects.all()

    @classmethod
    def export_data(cls, instance: Model) -> dict[str, Any]:
        raise NotImplementedError()

    @classmethod
    def load_from_file(cls, file_name: str, format: str) -> None:
        format = format.lower()
        assert format in FORMAT_ENUM, 'Incorrect format value'
        if format == JSON_FORMAT:
            cls._load_from_json(file_name)
            return
        cls._load_from_csv(file_name)

    @classmethod
    def save_to_file(cls, file_name: str, format: str) -> None:
        format = format.lower()
        assert format in FORMAT_ENUM, 'Incorrect format value'
        queryset = cls.export_queryset()
        if format == JSON_FORMAT:
            cls._save_to_json(file_name, queryset)
            return
        cls._save_to_csv(file_name, queryset)

    @classmethod
    def _load_from_csv(cls, file_name: str) -> None:
        with open(file_name) as file:
            reader = csv.DictReader(file)
            for row in reader:
                cls.import_data(row)

    @classmethod
    def _save_to_csv(cls, file_name: str, queryset: QuerySet) -> None:
        fieldnames = cls.export_fieldnames()
        with open(file_name, mode='w') as file:
            writer = csv.DictWriter(file, fieldnames)
            writer.writeheader()
            for instance in queryset:
                writer.writerow(cls.export_data(instance))

    @classmethod
    def _load_from_json(cls, file_name: str) -> None:
        with open(file_name) as file:
            data = json.load(file)
        for item in data:
            cls.import_data(item)

    @classmethod
    def _save_to_json(cls, file_name: str, queryset: QuerySet) -> None:
        data = []
        for instance in queryset:
            item = cls.export_data(instance)
            data.append(item)
        with open(file_name, mode='w') as file:
            json.dump(data, file)
