from django.core.management.base import BaseCommand, CommandError

from accept_requests.process_msg import process_msg


class Command(BaseCommand):
    help = 'Gives the retry mechanism'

    #def add_arguments(self, parser):
    #    parser.add_argument('poll_id', nargs='+', type=int)

    def handle(self, *args, **options):
        process_msg()