from django.core.management.base import BaseCommand, CommandError
from pymerlin import merlin
from merlin_api import pymerlin_adapter
from merlin_api.models import Simulation


class Command(BaseCommand):

    help = 'Adds the supplied scenario objects to the database simulation'

    def add_arguments(self, parser):
        parser.add_argument('simulation_id', nargs=1, type=int)
        parser.add_argument('scenario_list', nargs='+', type=merlin.Scenario)

    def handle(self, *args, **options):
        # try to retrieve db sim
        try:
            sim = Simulation.objects.get(pk=options['simulation_id'])
        except Simulation.DoesNotExist:
            raise CommandError(
                'There is no simulation with id {0} in the database'.format(
                    options['simulation_id']))
        # Simulation exists so now add the scenarios
        for s in options['scenario_list']:
            pymerlin_adapter.pymerlin_scenario2django(s, sim)

        self.stdout.write("Scenarios added successfully!")
