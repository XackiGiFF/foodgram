import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from recipes.management.reader.file_reader import TAGS_MANAGER, FileReader

DATA_ROOT = os.path.join(settings.BASE_DIR, 'data')


class Command(BaseCommand):
    help = 'Импортирование тегов'

    def add_arguments(self, parser):
        parser.add_argument('filename', default='tags.csv', nargs='?',
                            type=str)

    def handle(self, *args, **options):
        try:
            with open(os.path.join(DATA_ROOT, options['filename']), 'r',
                      encoding='utf-8') as file:
                reader = FileReader(file, TAGS_MANAGER)
                reader.read_file()
        except FileNotFoundError:
            raise CommandError('Добавьте файл tags в директорию data')
