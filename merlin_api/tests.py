from django.test import TestCase
from . import pymerlin_adapter
from .models import Simulation
from .merlin_test_processes import *
# from pymerlin.processes import *


# Create your tests here.

def create_test_simulation() -> merlin.Simulation:
    sim = merlin.Simulation(
        ruleset=None,
        config=[],
        outputs=set(),
        name='test_sim')

    # Configure sim properties
    sim.set_time_span(10)
    sim.add_attributes(['budget', 'capability', 'fixed_asset'])
    sim.add_unit_types(['$', 'desks', 'requests_handled'])

    sim_output = merlin.Output('requests_handled', name='requests handled')
    sim.outputs.add(sim_output)

    # Create Entities
    e_budget = merlin.Entity(
        name='Budget',
        attributes={'budget'})

    e_call_center = merlin.Entity(
        name='call center',
        attributes={'capability'})

    e_office = merlin.Entity(
        name='office building',
        attributes={'capability', 'fixed_asset'})

    sim.add_entities([e_budget, e_call_center, e_office])
    sim.set_source_entities([e_budget])

    # Create Entity Connectons
    # Budget connections
    sim.connect_entities(e_budget, e_call_center, '$')
    sim.connect_entities(e_budget, e_office, '$')

    # Call center connections
    sim.connect_output(e_call_center, sim_output)

    # Office connections
    sim.connect_entities(e_office, e_call_center, 'desks')

    # Add entity processes
    p_budget = BudgetProcess(name='Budget')
    p_staff = CallCenterStaffProcess(name='Call Center Staff')
    p_building = BuildingMaintainenceProcess(name='Building Maintenance')
    e_budget.add_process(p_budget)
    e_call_center.add_process(p_staff)
    e_office.add_process(p_building)
    return sim


class PymerlinRunTest(TestCase):

    def setUp(self):
        self.sim = create_test_simulation()

    def test_output(self):
        self.sim.run()
        result = list(self.sim.outputs)[0].result
        expected_result = \
            [20.0, 40.0, 60.0, 80.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0]

        for i in range(0, len(result)):
            self.assertAlmostEqual(result[i], expected_result[i])

    def test_input_requirement_exception(self):
        ccs = self.sim.get_process_by_name('Call Center Staff')
        salary_prop = ccs.get_prop('staff_salary')
        salary_prop.set_value(6.00)
        self.sim.run()
        errors = self.sim.get_last_run_errors()
        print(errors)
        first = errors[0]
        self.assertEqual(len(errors), 10)
        self.assertEqual(first.process, ccs)
        self.assertEqual(first.process_input, ccs.inputs['$'])
        self.assertEqual(first.input_value, 500.0)
        self.assertEqual(first.value, 600.0)


class Pymerlin2DjangoTestCase(TestCase):

    def setUp(self):
        self.sim = create_test_simulation()

    def test_simple_model_storage(self):
        pymerlin_adapter.pymerlin2django(self.sim)
        s = Simulation.objects.filter(name='test_sim')
        self.assertEqual(len(s), 1)


class Django2PymerlinTestCase(TestCase):

    def setUp(self):
        self.sim = create_test_simulation()

    def test_retrieve_and_run(self):
        pymerlin_adapter.pymerlin2django(self.sim)
        s = Simulation.objects.filter(name='test_sim')
        m = pymerlin_adapter.django2pymerlin(s[0])
        m.run()
        result = list(self.sim.outputs)[0].result
        expected_result = \
            [20.0, 40.0, 60.0, 80.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0]

        for i in range(0, len(result)):
            self.assertAlmostEqual(result[i], expected_result[i])
