import csv
from pathlib import Path

from django.core.management.base import BaseCommand
from reviews.models import (Category, Comment, Genre, Review, Title,
                            TitleGenre, User)

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
FILES_MODELS = {'users.csv': User,
                'category.csv': Category,
                'genre.csv': Genre,
                'titles.csv': Title,
                'genre_title.csv': TitleGenre,
                'review.csv': Review,
                'comments.csv': Comment}

INSTANCE_FIELDS = {'category': Category,
                   'author': User,
                   'title': Title,
                   'review': Review}


class Command(BaseCommand):
    """Скрипт загрузки в базу данных в формате csv.
    Запуск командой: python manage.py load_db
    """

    def handle(self, *args, **options):
        for name, model in FILES_MODELS.items():
            with open(
                    fr'{BASE_DIR}\static\data\{name}',
                    encoding='utf-8') as file:
                reader = csv.reader(file)
                fields = next(reader)
                for line in reader:
                    new_obj = model()
                    for count, item in enumerate(line):
                        key = fields[count]
                        if key in INSTANCE_FIELDS:
                            setattr(
                                new_obj, key, INSTANCE_FIELDS[key](pk=item)
                            )
                        else:
                            setattr(new_obj, key, item)
                    new_obj.save()
