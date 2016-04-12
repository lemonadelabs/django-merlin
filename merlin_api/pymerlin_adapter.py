from typing import MutableSequence, Mapping, Any
from merlin_api import models
from merlin_api.models import Simulation
from .merlin_test_processes import *

# An interface between the Django db model and the pymerlin module


def run_simulation(
        sim: models.Simulation) -> MutableSequence[Mapping[str, Any]]:
    """
    Runs the supplied simulation and returns the resulting telemetry data
    :param sim:
    :return:
    """
    msim = django2pymerlin(sim)
    # msim = tests.create_test_simulation()
    msim.run()
    return msim.get_sim_telemetry()


def delete_django_sim(sim_id: int) -> None:
    """
    Deletes the django simulation model from the
    database without violating integrity constraints.
    """
    sim = Simulation.objects.get(pk=sim_id)
    sim.entities.all().delete()
    sim.outputs.all().delete()
    sim.delete()


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
            mproc_class = globals()[p.process_class]
            mproc = mproc_class()
            mproc.priority = p.priority
            mproc.id = p.id

            # load in the process property values
            for pprop in p.properties.all():
                mpprop = mproc.get_prop(pprop.name)
                mpprop.id = pprop.id
                mpprop.max_val = pprop.max_value
                mpprop.min_val = pprop.min_value
                mpprop.set_value(pprop.property_value)

            mentities[e.id].add_process(mproc)

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


def pymerlin2django(sim: merlin.Simulation) -> None:
    """
    Inserts the simulation object into the django
    database by creating the required django model
    instances.
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
            dprocess.process_class = p.__class__.__name__
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
