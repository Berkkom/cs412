# File: load_data.py
# Author: Berk Komurcuoglu (berkkom@bu.edu) 4/3/2026
# Description: Django management command to populate the database with
# initial Joke and Picture data. Usage: python manage.py load_data

from django.core.management.base import BaseCommand
from dadjokes.models import Joke, Picture


class Command(BaseCommand):
    """Management command to load initial dad jokes and pictures into the database."""
    help = 'Load initial Joke and Picture data into the database.'

    def handle(self, *args, **options):

        jokes_data = [
            {
                'text': 'Why do cows have hooves instead of feet? Because they lactose.',
                'contributor': 'DadJokeMaster',
            },
            {
                'text': 'What do you call the assistant to the assistant nut? Co-co-nut.',
                'contributor': 'DadJokeMaster',
            },
            {
                'text': "You know why you shouldn't play hide and seek with mountains? Because they are always peaking.",
                'contributor': 'DadJokeMaster',
            },
            {
                'text': 'Why was everyone tired on April 1? Because they just finished a long 31 day March.',
                'contributor': 'DadJokeMaster',
            },
            {
                'text': 'Would anyone be interested in being my companion? Asking for a friend.',
                'contributor': 'DadJokeMaster',
            },
            {
                'text': 'What genre are national anthems? Country.',
                'contributor': 'DadJokeMaster',
            },
            {
                'text': 'Fun fact: Koi fish always travel in groups of 4. If attacked, the A, B, and C koi will scatter, leaving behind the D koi.',
                'contributor': 'DadJokeMaster',
            },
        ]

        pictures_data = [
            {
                'image_url': 'https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExYmxpd3ppNzQ2a2ZwOTN1ZW9kcnRuZGwxZXFlZjJ3amJkdGMyajM3biZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/XHeLeuirRbwptHhSWd/giphy.gif',
                'contributor': 'GifLord',
            },
            {
                'image_url': 'https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExNGdtYzFtNjcxa3k4b2ptYTBpdGxyOWxoaWZuaWRtaGQ5MTlma25tdyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/M7t5GIszd4Nc4/giphy.gif',
                'contributor': 'GifLord',
            },
            {
                'image_url': 'https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExNWVmMXU0cmtmOXJxNnIzeHF2YTdtMGM3bm9uYmJhY2d6dWt6cGR2ZSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/d4CnuaS1BQl7W5nowu/giphy.gif',
                'contributor': 'MemeMaster',
            },
            {
                'image_url': 'https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExczN5YzdmaGRpazR3dndpamZ1ZHQ4MTZ2cHpzMmljczdjaDlxY2IxeCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/0uBL9HqP48Nu1DNr7r/giphy.gif',
                'contributor': 'MemeMaster',
            },
            {
                'image_url': 'https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExOXllN20zOTB0OGFjbHMyMjZ6ZDRnbnp4OHozNzVjeXkxNmZram94MCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/enCWEo0vG25Ow/giphy.gif',
                'contributor': 'FunnyPics',
            },
        ]

        for joke_data in jokes_data:
            joke, created = Joke.objects.get_or_create(
                text=joke_data['text'],
                defaults={'contributor': joke_data['contributor']},
            )
            status = 'Created' if created else 'Already exists'
            self.stdout.write(f'  {status}: {joke_data["text"][:50]}...')

        for pic_data in pictures_data:
            pic, created = Picture.objects.get_or_create(
                image_url=pic_data['image_url'],
                defaults={'contributor': pic_data['contributor']},
            )
            status = 'Created' if created else 'Already exists'
            self.stdout.write(f'  {status}: {pic_data["image_url"][:50]}...')

        self.stdout.write(self.style.SUCCESS('Done loading data!'))