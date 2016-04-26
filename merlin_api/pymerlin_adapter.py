import logging
import importlib
from typing import MutableSequence, Mapping, Any, List

import pymerlin

from merlin_api import models
from merlin_api.models import Simulation, Scenario
from pymerlin import merlin
from pymerlin.processes import *

logger = logging.getLogger('merlin_api.pymerlin_adapter')

# An interface between the Django db model and the pymerlin module


def run_simulation(
        sim: models.Simulation,
        scenarios: List[models.Scenario]=list()) -> \
        MutableSequence[Mapping[str, Any]]:
    """
    Runs the supplied simulation and returns the resulting telemetry data
    :param sim:
    :param scenarios: A set of scenarios to run on the sim
    :return:
    """

    msim = django2pymerlin(sim)
    m_scenarios = list()

    if scenarios:
        for ds in scenarios:
            ms = django_scenario2pymerlin(ds, msim)
            m_scenarios.append(ms)

    # msim = tests.create_test_simulation()
    msim.run(scenarios=m_scenarios)
    return msim.get_sim_telemetry()


def pymerlin_scenario2django(
        scenario: merlin.Scenario,
        sim: models.Simulation) -> models.Scenario:
    """
    Converts a merlin.Scenario into a django model representation
    and saves the result into the database.
    :param scenario: The merlin.Scenario to convert
    :param sim: The simulation to relate the scenario to
    :return:
    """

    ds = models.Scenario()
    ds.sim = sim
    ds.name = scenario.name
    ds.start_offset = scenario.start_offset
    ds.save()

    # Add the events
    for e in scenario.events:
        de = models.Event()
        de.scenario = ds
        de.actions = e.actions
        de.time = e.time
        de.save()

    return ds


def django_scenario2pymerlin(
        scenario: models.Scenario,
        sim: merlin.Simulation) -> merlin.Scenario:
    """
    Converts a django-merlin scenario into a pymerlin one
    :param scenario: The django scenario model instance
    :param sim: the already deserialised simulation to relate the
    scenario to.
    :return: The merlin.Scenario representation
    """

    s = merlin.Scenario(sim, set())
    s.id = scenario.id
    s.name = scenario.name

    p_events = set()
    for e in scenario.events.all():
        p_event = merlin.Event.create(e.time, e.actions)
        p_event.id = e.id
        p_event.name = e.name
        p_events.add(p_event)

    s.events = p_events
    return s


def delete_django_sim(sim_id: int) -> None:
    """
    Deletes the django simulation model from the
    database without violating integrity constraints.
    """
    sim = Simulation.objects.get(pk=sim_id)
    sim.entities.all().delete()
    sim.outputs.all().delete()
    sim.delete()


def get_fullname_from_process_class(the_class: type) -> str:
    """
    :param type the_class: a subclass from merlin.Process
    :returns: import path incl modules and class name
    :rtype: str

    Constructs the import path string, which allows importing the process class
    to a later point in time with :py:func:`.get_process_class_from_fullname`.

    .. note::

        The result will depend on the linkage of source code
        (symlink or entry in sys.path)
        and method of importing the process class.
    """
    if not issubclass(the_class, merlin.Process):
        raise TypeError("expecting sub class of merlin.Process")
    proc_classname = the_class.__name__
    proc_module = the_class.__module__
    return "%s.%s" % (proc_module, proc_classname)


def get_process_class_from_fullname(the_name: str) -> type:
    """
    :param str the_name: name used to import the module and find the
       merlin.Process subclass
    :returns: the class (not the object!)
    
    This is the inverse of the :py:func:`.get_process_class_from_fullname`.
    """
    # split name into parts
    mod_path = the_name.split(".")[:-1]
    if len(mod_path):
        try:
            namespace = importlib.import_module(".".join(mod_path)).__dict__
        except ImportError:
            raise ValueError(
                'module containing process class %s could not be imported'
                % the_name)
    else:
        # don't like this!
        namespace = globals()
    class_def = the_name.split(".")[-1]
    if class_def not in namespace:
            raise ValueError('process class %s not found' % the_name)

    # execute this function
    return namespace[class_def]


def django2pymerlin(sim: models.Simulation) -> merlin.Simulation:
    """
    Instantiates a merlin.Simulation from a django model sim
    :type sim: models.Simulation
    :param sim:
    :return merlin.Simulation:
    """

    # Simulation
    msim = merlin.Simulation()
    msim.set_time_span(sim.num_steps)
    msim.name = sim.name

    # Attributes
    msim.add_attributes([a.value for a in sim.attributes.all()])

    # Unit Types
    msim.add_unit_types([u.value for u in sim.unittypes.all()])

    # Outputs
    moutputs = dict()
    for o in sim.outputs.all():
        moutput = merlin.Output(o.unit_type.value, name=o.name)
        moutput.id = o.id
        moutputs[o.id] = moutput
        msim.add_output(moutput)

    # Entities
    smentities = list()
    mentities = dict()

    for e in sim.entities.all():
        mentity = merlin.Entity(
            msim,
            name=e.name,
            attributes=set(e.attributes))
        if e.is_source:
            smentities.append(mentity)
        mentity.id = e.id
        mentities[e.id] = mentity

    msim.add_entities(mentities.values())
    msim.set_source_entities(smentities)

    # add parent relationships
    for e in sim.entities.all():
        if e.parent:
            child = mentities[e.id]
            parent = mentities[e.parent.id]
            msim.parent_entity(parent, child)

    # Sim Connections
    for e in sim.entities.all():
        for o in e.outputs.all():
            for ep in o.endpoints.all():
                if ep.input is None:
                    # Connect to an output
                    msim.connect_output(
                        mentities[e.id],
                        moutputs[ep.sim_output.parent.id],
                        ep.sim_output.additive_write,
                        merlin.OutputConnector.ApportioningRules(
                            o.apportion_rule))
                else:
                    # Connect to another entity
                    msim.connect_entities(
                        mentities[e.id],
                        mentities[ep.input.parent.id],
                        o.unit_type.value,
                        ep.input.additive_write,
                        merlin.OutputConnector.ApportioningRules(
                            o.apportion_rule))

        t_o = len(mentities[e.id].outputs)

        for p in e.processes.all():
            mproc_class = get_process_class_from_fullname(p.process_class)
            mproc = mentities[e.id].create_process(
                mproc_class,
                p.parameters,
                p.priority)   # type: merlin.Process
            mproc.id = p.id

            for mproc_output in mproc.outputs.values():
                match = False
                for mi in mentities[e.id].outputs:
                    if mi.type == mproc_output.type:
                        match = True
                        break

                if not match:
                    logging.error("""output missmatch: process= {0} output= {1}
                    has no matching output in entity= {2}""".format(
                        mproc,
                        mproc_output,
                        mentities[e.id]))

            # load in the process property values
            for pprop in p.properties.all():
                mpprop = mproc.get_prop(pprop.name)
                assert mpprop is not None
                mpprop.id = pprop.id
                mpprop.max_val = pprop.max_value
                mpprop.min_val = pprop.min_value
                mpprop.set_value(pprop.property_value)

        t_o2 = len(mentities[e.id].outputs)
        assert t_o == t_o2

    # rewrite input and output connector ids

    for dso in sim.outputs.all():
        for di in dso.inputs.all():
            for i in moutputs[dso.id].inputs:
                if i.source.parent.id == di.source.parent.id:
                    i.id = di.id

    for e in sim.entities.all():
        for o in e.outputs.all():
            for mout_con in mentities[e.id].outputs:
                if mout_con.type == o.unit_type.value:
                    mout_con.id = o.id
                for ep in o.endpoints.all():
                    dinput = ep.input
                    if ep.input:
                        for mendpoint in mout_con.get_endpoints():
                            minput = mendpoint[0]
                            if minput.parent.id == dinput.parent.id:
                                minput.id = dinput.id

    return msim


def pymerlin2django(sim: merlin.Simulation) -> int:
    """
    Inserts the simulation object into the django
    database by creating the required django model
    instances.

    :returns: the id for this simulation within the database
    """

    # Simulation
    dsim = models.Simulation()
    dsim.num_steps = sim.num_steps
    dsim.name = sim.name
    dsim.save()

    # Attributes
    for a in sim.get_attributes():
        da = models.Attribute()
        da.sim = dsim
        da.value = a
        da.save()

    ut_map = dict()

    # Unit Types
    for ut in sim.get_unit_types():
        dut = models.UnitType()
        dut.sim = dsim
        dut.value = ut
        ut_map[ut] = dut
        dut.save()

    output_map = dict()

    # Outputs
    for o in sim.outputs:
        doutput = models.Output()
        doutput.name = o.name
        doutput.sim = dsim
        assert o.sim is not None
        doutput.unit_type = ut_map[o.type]
        doutput.save()
        output_map[o.id] = doutput

    # Entities
    entity_map = dict()

    for e in sim.get_entities():
        dentity = models.Entity()
        dentity.name = e.name
        dentity.sim = dsim
        dentity.attributes = list(e.attributes)
        dentity.is_source = (e in sim.source_entities)
        dentity.save()
        entity_map[e.id] = dentity

    # Create entity -> Entity relations
    for e in sim.get_entities():
        if e.parent:
            child = entity_map[e.id]
            parent = entity_map[e.parent.id]
            child.parent = parent
            child.save()

    input_con_map = dict()
    output_con_map = dict()

    # Create Inputs and Outputs
    for e in sim.get_entities():
        for i in e.inputs:
            dinput_con = models.InputConnector()
            dinput_con.parent = entity_map[e.id]
            dinput_con.additive_write = i.additive_write
            dinput_con.name = i.name
            dinput_con.unit_type = ut_map[i.type]
            dinput_con.save()
            input_con_map[i.id] = dinput_con
        for o in e.outputs:
            doutput_con = models.OutputConnector()
            doutput_con.parent = entity_map[e.id]
            doutput_con.unit_type = ut_map[o.type]
            doutput_con.name = o.name
            doutput_con.apportion_rule = o.apportioning.value
            doutput_con.save()
            output_con_map[o.id] = doutput_con

    for op in sim.outputs:
        for i in op.inputs:
            dinput_con = models.SimOutputConnector()
            dinput_con.parent = output_map[op.id]
            dinput_con.additive_write = i.additive_write
            dinput_con.name = i.name
            dinput_con.unit_type = ut_map[i.type]
            dinput_con.source = output_con_map[i.source.id]
            dinput_con.save()
            input_con_map[i.id] = dinput_con

    # Create Input source references and Endpoint references
    for e in sim.get_entities():
        for i in e.inputs:
            i_con = input_con_map[i.id]
            # Foo
            if i.source is None:
                logger.error(
                    """
                        Input has no source reference!

                        ENTITY:
                            {0}

                        INPUT:
                            {1}""".format(e, i))
            source = output_con_map[i.source.id]
            i_con.source = source
            i_con.save()
        for o in e.outputs:
            for ep in o.get_endpoints():
                dendpoint = models.Endpoint()
                dendpoint.parent = output_con_map[o.id]
                dendpoint.bias = ep[1]
                # print('#### {0}: {1}'.format(ep[0].id, ep[0]))
                if isinstance(input_con_map[ep[0].id], models.InputConnector):
                    dendpoint.input = input_con_map[ep[0].id]
                else:
                    dendpoint.sim_output = input_con_map[ep[0].id]

                dendpoint.save()

    # Create Processes
    for e in sim.get_entities():
        for p in e.get_processes():
            dprocess = models.Process()
            dprocess.parent = entity_map[e.id]
            dprocess.name = p.name
            dprocess.priority = p.priority
            dprocess.process_class = get_fullname_from_process_class(type(p))
            dprocess.parameters = p.default_params
            dprocess.save()

            # Create Process Properties
            pps = p.get_properties()
            for ps in pps:
                dps = models.ProcessProperty()
                dps.name = ps.name
                dps.process = dprocess
                dps.property_type = ps.type.value
                dps.default_value = ps.default
                if ps.max_val:
                    dps.max_value = ps.max_val
                if ps.min_val:
                    dps.min_value = ps.min_val
                dps.property_value = ps.get_value()
                dps.save()
    return dsim.id
