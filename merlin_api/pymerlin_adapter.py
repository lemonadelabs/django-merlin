from pymerlin import merlin
from merlin_api import models

# An interface between the Django db model and the pymerlin module


def delete_django_sim(sim: models.Simulation) -> None:
    """
    Deletes the django simulation model from the
    database without violating integrity constraints.
    """

    sim.entity_set.all().delete()
    sim.output_set.all().delete()
    sim.delete()


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
