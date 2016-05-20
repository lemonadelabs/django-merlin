import json
import argparse
from django.core.management.base import BaseCommand, CommandError
from merlin_api.models import Simulation


class Command(BaseCommand):

    help = '''Restores entity positions from a file created by savelayout'''

    def add_arguments(self, parser):
        parser.add_argument('simulation_id', type=int)
        parser.add_argument('file_path', type=argparse.FileType('r'))

    def handle(self, *args, **options):
        try:
            sim = Simulation.objects.get(pk=options['simulation_id'])
        except Simulation.DoesNotExist:
            raise CommandError(
                'There is no simulation with id {0} in the database'.format(
                    options['simulation_id']))

        # try and parse json
        try:
            json_data = options['file_path'].read()
            data = json.loads(json_data)
        except:
            raise CommandError(
                'There was an error loading the data from the file')

        for e in sim.entities.all():
            # Try to find matching positional info
            for pos_data in data:
                name_match = (pos_data['name'] == e.name)
                if e.parent is None:
                    parent_match = (pos_data['parent'] is None)
                else:
                    parent_match = (pos_data['parent'] == e.parent.name)

                if name_match and parent_match:
                    e.display_pos_x = pos_data['x']
                    e.display_pos_y = pos_data['y']
                    e.save()

        for o in sim.outputs.all():
            for pos_data in data:
                name_match = (pos_data['name'] == o.name)
                if name_match:
                    o.display_pos_x = pos_data['x']
                    o.display_pos_y = pos_data['y']
                    o.save()

        self.stdout.write(
            self.style.SUCCESS(
                'Successfully loaded layout info'))
