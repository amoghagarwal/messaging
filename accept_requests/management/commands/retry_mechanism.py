from django.core.management.base import BaseCommand, CommandError

from accept_requests.callback_service import Callbacks


class Command(BaseCommand):
    help = 'Gives the retry mechanism'

    #def add_arguments(self, parser):
    #    parser.add_argument('poll_id', nargs='+', type=int)

    def handle(self, *args, **options):
        callback = Callbacks()
        callback.fetch_msg_from_queue()