from django.test import TestCase
from . import pymerlin_adapter
from .models import *
from pymerlin.processes import *
import json

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
    sim.add_output(sim_output)

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


class EntityModelTest(TestCase):

    def setUp(self):
        sim = create_test_simulation()
        pymerlin_adapter.pymerlin2django(sim)

    def test_update_position(self):
        e = Entity.objects.all()[0]
        response = self.client.get('/api/entities/{0}/'.format(e.id))

        j = json.loads(response.content.decode("utf-8"))
        j['display_pos_x'] = 100.0
        j['display_pos_y'] = 100.0
        j['description'] = "foo"
        put_response = self.client.put(
            '/api/entities/{0}/'.format(e.id),
            content_type='application/json',
            data=json.dumps(j))
        print(put_response.status_code)
        print(put_response.content)


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
        salary_prop = ccs.get_prop('staff salary')
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
        pymerlin_adapter.pymerlin2django(self.sim)
        self.dsim = Simulation.objects.filter(name='test_sim')[0]

    def test_sim_integrity(self):
        self.assertEqual(self.sim.num_steps, self.dsim.num_steps)

    def test_entity_integrity(self):

        self.assertEqual(
            len(self.dsim.entities.all()),
            len(self.sim.get_entities()))
        for de in self.dsim.entities.all():
            matched_entity = None
            for e in self.sim.get_entities():
                if e.name == de.name:
                    matched_entity = e
            self.assertIsNotNone(matched_entity)
            self.assertIsNone(de.parent)
            self.assertIsNone(e.parent)
            self.assertEqual(e.parent, de.parent)
            if de.name == 'Budget':
                self.assertTrue(de.is_source)
                self.assertTrue(matched_entity in self.sim.source_entities)

    def test_entity_output_connections(self):
        for e in self.sim.get_entities():
            matched_entity = None
            for ed in self.dsim.entities.all():
                if ed.name == e.name:
                    matched_entity = ed
            self.assertIsNotNone(matched_entity)
            # Make sure that for every output in sim there is exactly one in dsim
            self.assertEqual(
                len(e.outputs),
                len(matched_entity.outputs.all()))

            # Output testing

            for o in e.outputs:
                self.assertIsNotNone(o.parent)
                matched_output = None
                for od in matched_entity.outputs.all():
                    if od.unit_type.value == o.type:
                        matched_output = od
                self.assertIsNotNone(matched_output)
                self.assertIsNotNone(matched_output.parent)
                self.assertEqual(matched_output.name, o.name)
                # Check that the endpoints of the output match the pymerlin sim
                self.assertEqual(
                    len(o.get_endpoints()),
                    len(matched_output.endpoints.all()))
                for ep in o.get_endpoints():
                    input_c = ep[0]
                    bias = ep[1]
                    matched_endpoint = None
                    for dep in matched_output.endpoints.all():
                        if (
                                dep.input and
                                dep.input.name == input_c.name and
                                input_c.parent.name == dep.input.parent.name):
                            matched_endpoint = dep
                            self.assertIsNone(dep.sim_output)
                            self.assertEqual(
                                input_c.parent.name,
                                matched_endpoint.input.parent.name)
                        elif (
                                dep.sim_output and
                                dep.sim_output.name == input_c.name and
                                input_c.parent.name == dep.sim_output.parent.name):
                            matched_endpoint = dep
                            self.assertIsNone(dep.input)
                            self.assertEqual(
                                input_c.parent.name,
                                matched_endpoint.sim_output.parent.name)
                    self.assertIsNotNone(matched_endpoint)
                    self.assertEqual(bias, matched_endpoint.bias)

    def test_entity_input_connections(self):
        for e in self.sim.get_entities():
            matched_entity = None
            for ed in self.dsim.entities.all():
                if ed.name == e.name:
                    matched_entity = ed
            self.assertIsNotNone(matched_entity)
            # Make sure that for every input in sim there is exactly one in dsim
            self.assertEqual(len(e.inputs), len(matched_entity.inputs.all()))

            for i in e.inputs:
                self.assertIsNotNone(i.parent)
                matched_input = None

                for dinput_con in matched_entity.inputs.all():
                    if dinput_con.unit_type.value == i.type:
                        matched_input = dinput_con
                self.assertIsNotNone(matched_input)
                self.assertIsNotNone(matched_input.source)
                self.assertEqual(matched_input.source.parent.name, i.source.parent.name)
                self.assertEqual(matched_input.unit_type.value, i.type)
                self.assertEqual(matched_input.name, i.name)

    def test_sim_output_integrity(self):
        self.assertEqual(len(self.sim.outputs), 1)
        for o in self.sim.outputs:
            matched_output = None
            self.assertEqual(len(self.sim.outputs), len(self.dsim.outputs.all()))
            for doutput in self.dsim.outputs.all():
                if doutput.name == o.name:
                    matched_output = doutput
            self.assertIsNotNone(matched_output)
            self.assertEqual(matched_output.unit_type.value, o.type)
            self.assertIsNotNone(o.sim)
            self.assertIsNotNone(matched_output.sim)
            self.assertEqual(matched_output.sim.name, o.sim.name)
            self.assertEqual(len(o.inputs), len(matched_output.inputs.all()))
            for i in o.inputs:
                matched_input = None
                for din in matched_output.inputs.all():
                    if din.parent.name == i.parent.name:
                        matched_input = din
                self.assertIsNotNone(matched_input)
                self.assertEqual(matched_input.name, i.name)
                self.assertEqual(matched_input.unit_type.value, i.type)


class Django2PymerlinTestCase(TestCase):


    def setUp(self):
        s = create_test_simulation()
        pymerlin_adapter.pymerlin2django(s)
        self.dsim = Simulation.objects.filter(name='test_sim')[0]
        self.sim = pymerlin_adapter.django2pymerlin(self.dsim)

    def tearDown(self):
        pymerlin_adapter.delete_django_sim(self.dsim.id)

    def test_sim_integrity(self):
        self.assertEqual(self.sim.num_steps, self.dsim.num_steps)

    def test_entity_integrity(self):
        self.assertEqual(
            len(self.dsim.entities.all()),
            len(self.sim.get_entities()))
        for de in self.dsim.entities.all():
            matched_entity = None
            for e in self.sim.get_entities():
                if e.id == de.id:
                    matched_entity = e
            self.assertIsNotNone(matched_entity)
            self.assertIsNone(de.parent)
            self.assertIsNone(e.parent)
            self.assertEqual(e.parent, de.parent)
            if de.name == 'Budget':
                self.assertTrue(de.is_source)
                self.assertTrue(matched_entity in self.sim.source_entities)

    def test_entity_output_connections(self):
        for e in self.sim.get_entities():
            matched_entity = None
            for ed in self.dsim.entities.all():
                if ed.id == e.id:
                    matched_entity = ed
            self.assertIsNotNone(matched_entity)
            # Make sure that for every output in sim there is exactly one in dsim
            self.assertEqual(
                len(e.outputs),
                len(matched_entity.outputs.all()),
                "dserialised entity with extra output: {0}".format(e))

            # Output testing

            for o in e.outputs:
                self.assertIsNotNone(o.parent)
                matched_output = None
                for od in matched_entity.outputs.all():
                    if od.id == o.id:
                        matched_output = od
                self.assertIsNotNone(matched_output)
                self.assertIsNotNone(matched_output.parent)
                self.assertEqual(matched_output.name, o.name)
                # Check that the endpoints of the output match the pymerlin sim
                self.assertEqual(
                    len(o.get_endpoints()),
                    len(matched_output.endpoints.all()))
                for ep in o.get_endpoints():
                    input_c = ep[0]
                    bias = ep[1]
                    matched_endpoint = None
                    for dep in matched_output.endpoints.all():
                        if (
                                        dep.input and
                                            dep.input.id == input_c.id):
                            matched_endpoint = dep
                            self.assertIsNone(dep.sim_output)
                            self.assertEqual(
                                input_c.parent.name,
                                matched_endpoint.input.parent.name)
                        elif (
                                        dep.sim_output and
                                            dep.sim_output.id == input_c.id):
                            matched_endpoint = dep
                            self.assertIsNone(dep.input)
                            self.assertEqual(
                                input_c.parent.name,
                                matched_endpoint.sim_output.parent.name)
                    self.assertIsNotNone(matched_endpoint)
                    self.assertEqual(bias, matched_endpoint.bias)

    def test_entity_input_connections(self):
        for e in self.sim.get_entities():
            matched_entity = None
            for ed in self.dsim.entities.all():
                if ed.id == e.id:
                    matched_entity = ed
            self.assertIsNotNone(matched_entity)
            # Make sure that for every input in sim there is exactly one in dsim
            self.assertEqual(len(e.inputs), len(matched_entity.inputs.all()))

            for i in e.inputs:
                self.assertIsNotNone(i.parent)
                matched_input = None

                for dinput_con in matched_entity.inputs.all():
                    if dinput_con.id == i.id:
                        matched_input = dinput_con
                self.assertIsNotNone(matched_input)
                self.assertIsNotNone(matched_input.source)
                self.assertEqual(matched_input.source.parent.name,
                                 i.source.parent.name)
                self.assertEqual(matched_input.unit_type.value, i.type)
                self.assertEqual(matched_input.name, i.name)

    def test_sim_output_integrity(self):
        self.assertEqual(len(self.sim.outputs), 1)
        for o in self.sim.outputs:
            matched_output = None
            self.assertEqual(len(self.sim.outputs),
                             len(self.dsim.outputs.all()))
            for doutput in self.dsim.outputs.all():
                if doutput.id == o.id:
                    matched_output = doutput
            self.assertIsNotNone(matched_output)
            self.assertEqual(matched_output.unit_type.value, o.type)
            self.assertIsNotNone(o.sim)
            self.assertIsNotNone(matched_output.sim)
            self.assertEqual(matched_output.sim.name, o.sim.name)
            self.assertEqual(len(o.inputs), len(matched_output.inputs.all()))
            for i in o.inputs:
                matched_input = None
                for din in matched_output.inputs.all():
                    if din.parent.id == i.parent.id:
                        matched_input = din
                self.assertIsNotNone(matched_input)
                self.assertEqual(matched_input.unit_type.value, i.type)

    def test_retrieve_and_run(self):
        self.sim.run()
        result = list(self.sim.outputs)[0].result
        expected_result = \
            [20.0, 40.0, 60.0, 80.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0]

        self.assertEqual(len(result), len(expected_result))
        for i in range(0, len(result)):
            self.assertAlmostEqual(result[i], expected_result[i])
