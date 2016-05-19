import argparse
from merlin_api.models import *
import json
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):

    help = ('Saves entity position information to a file to be ' +
            'restored at a later date')

    def add_arguments(self, parser):
        parser.add_argument('simulation_id', type=int)
        parser.add_argument('file_path', type=argparse.FileType('w'))

    def handle(self, *args, **options):
        try:
            sim = Simulation.objects.get(pk=options['simulation_id'])
        except Simulation.DoesNotExist:
            raise CommandError(
                'There is no simulation with id {0} in the database'.format(
                    options['simulation_id']))

        # get all entities and store their positional info
        data = list()
        for e in sim.entities.all():
            pos_data = dict()
            pos_data['name'] = e.name
            pos_data['parent'] = None if not e.parent else e.parent.name
            pos_data['x'] = e.display_pos_x
            pos_data['y'] = e.display_pos_y
            data.append(pos_data)

        for o in sim.outputs.all():
            pos_data = dict()
            pos_data['name'] = o.name
            pos_data['parent'] = o.sim.name
            pos_data['x'] = o.display_pos_x
            pos_data['y'] = o.display_pos_y
            data.append(pos_data)

        json_data = json.dumps(data)

        try:
            options['file_path'].write(json_data)
            self.stdout.write(
                self.style.SUCCESS(
                    'Successfully saved layout info for model {0} to file {1}'.format(
                        options['simulation_id'],
                        options['file_path'])
                )
            )
        except:
            raise CommandError(
                'There was an error writing to the file. :('
            )
        finally:
            options['file_path'].close()
