from django.test import TestCase
from pymerlin import merlin
from . import pymerlin_adapter
from .models import Simulation


class BudgetProcess(merlin.Process):

    def __init__(self, name='Budget', start_amount=10000.00):
        super(BudgetProcess, self).__init__(name)

        # Define outputs
        p_output = merlin.ProcessOutput('output_$', '$', connector=None)

        # Define properties
        p_property = merlin.ProcessProperty(
            'amount',
            property_type=merlin.ProcessProperty.PropertyType.number_type,
            default=start_amount,
            parent=self)

        self.outputs = {'$': p_output}
        self.props = {'amount': p_property}

    def reset(self):
        # define internal instance variables on init
        self.current_amount = self.props['amount'].get_value()
        self.amount_per_step = self.current_amount / self.parent.sim.num_steps

    def compute(self, tick):
        if self.current_amount > 0.00:
            output = self.amount_per_step
            if output > self.current_amount:
                output = self.current_amount
            self.current_amount -= output
            self.outputs['$'].connector.write(output)
        else:
            self.outputs['$'].connector.write(0.00)


class CallCenterStaffProcess(merlin.Process):

    def __init__(self, name='Call Center Staff'):
        super(CallCenterStaffProcess, self).__init__(name)

        # Define inputs
        i_desks = merlin.ProcessInput('i_desks', 'desks', connector=None)
        i_funds = merlin.ProcessInput('i_$', '$', connector=None)

        # Define outputs
        o_requests_handled = merlin.ProcessOutput(
            'o_requests_handled',
            'requests_handled',
            connector=None)

        # Define properties
        p_staff = merlin.ProcessProperty(
            'staff number',
            property_type=merlin.ProcessProperty.PropertyType.number_type,
            default=100,
            parent=self)

        p_staff_salary = merlin.ProcessProperty(
            'staff salary',
            property_type=merlin.ProcessProperty.PropertyType.number_type,
            default=5.00,
            parent=self)

        p_staff_per_desk = merlin.ProcessProperty(
            'staff per desk',
            property_type=merlin.ProcessProperty.PropertyType.number_type,
            default=1,
            parent=self)

        p_months_to_train = merlin.ProcessProperty(
            'months to train',
            property_type=merlin.ProcessProperty.PropertyType.number_type,
            default=5,
            parent=self)

        self.props = {
            'staff_number': p_staff,
            'staff_salary': p_staff_salary,
            'staff_per_desk': p_staff_per_desk,
            'months_to_train': p_months_to_train}

        self.inputs = {'desks': i_desks, '$': i_funds}
        self.outputs = {'requests_handled': o_requests_handled}

    def reset(self):
        # Calculations that
        # you do not expect to change should be put in the
        # reset function as this is called only once at the
        # start of the simualtion run.
        self.desks_required = (
            self.props['staff_number'].get_value() /
            self.props['staff_per_desk'].get_value())
        self.funds_required = (
            self.props['staff_number'].get_value() *
            self.props['staff_salary'].get_value())
        self.maximal_output = self.props['staff_number'].get_value()
        self.train_slope = 1.0 / self.props['months_to_train'].get_value()

    def compute(self, tick):
        # check requirements
        if self.inputs['desks'].connector.value < self.desks_required:
            raise merlin.InputRequirementException(
                self,
                self.inputs['desks'],
                self.inputs['desks'].connector.value,
                self.desks_required)
        if self.inputs['$'].connector.value < self.funds_required:
            raise merlin.InputRequirementException(
                self,
                self.inputs['$'],
                self.inputs['$'].connector.value,
                self.funds_required)

        # compute outputs
        output = self.maximal_output * self._train_modifier(tick)
        self.inputs['desks'].consume(self.desks_required)
        self.inputs['$'].consume(self.funds_required)
        self.outputs['requests_handled'].connector.write(output)

    def _train_modifier(self, tick):
        # This is just a linear function with the
        # slope steepness = months to train
        mtt = self.props['months_to_train'].get_value()
        train_slope = 1.0 / float(mtt)
        if tick < mtt:
            return tick * train_slope
        else:
            return 1.0


class BuildingMaintainenceProcess(merlin.Process):
    def __init__(self, name='Building Maintenance'):
        super(BuildingMaintainenceProcess, self).__init__(name)

        # Define inputs
        i_funds = merlin.ProcessInput('i_$', '$', connector=None)

        # Define outputs
        o_desks = merlin.ProcessOutput('o_desks', 'desks', connector=None)

        # Define properties
        p_maintenance_cost = merlin.ProcessProperty(
            'monthly maintenance cost',
            property_type=merlin.ProcessProperty.PropertyType.number_type,
            default=500.00,
            parent=self)

        p_desks_provided = merlin.ProcessProperty(
            'desks provided',
            property_type=merlin.ProcessProperty.PropertyType.number_type,
            default=100.0,
            parent=self)

        self.props = {
            'cost': p_maintenance_cost,
            'desks': p_desks_provided}

        self.inputs = {'$': i_funds}
        self.outputs = {'desks': o_desks}

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

class Pymerlin2DjangoTestCase(TestCase):

    def setUp(self):
        self.sim = create_test_simulation()


    def test_simple_model_storage(self):
        pymerlin_adapter.pymerlin2django(self.sim)
        s = Simulation.objects.filter(name='test_sim')
        self.assertEqual(len(s), 1)
