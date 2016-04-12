from django.core.management.base import BaseCommand, CommandError
from merlin_api import pymerlin_adapter, tests
import pymerlin
import importlib

class Command(BaseCommand):
    help = 'add simulation created by a function in a module\n e.g. merlin_api.tests.create_test_simulation'

    def add_arguments(self, parser):
        parser.add_argument('module_name', nargs='+', type=str)

    def handle(self, *args, **options):
        for module_name in options['module_name']:
            try:
                # split name into parts
                mod_path=module_name.split(".")[:-1]
                if len(mod_path):
                    try:
                        namespace=importlib.import_module(".".join(mod_path)).__dict__
                    except ImportError:
                        raise CommandError('model %s could not be imported' % module_name)
                else:
                    namespace=globals()

                mod_func=module_name.split(".")[-1]
                if mod_func not in namespace:
                    raise CommandError('model creation function %s not found' % module_name)

                # execute this function
                sim = namespace[mod_func]()

            except Exception as e:
                raise CommandError('model creation %s failed' % module_name) from e

            if not isinstance(sim, pymerlin.merlin.Simulation):
                raise ValueError("unexpected return type")

            pymerlin_adapter.pymerlin2django(sim)
            self.stdout.write(self.style.SUCCESS('Successfully added "%s"' % module_name))
