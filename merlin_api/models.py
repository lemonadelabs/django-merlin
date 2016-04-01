from django.db import models
from django.contrib.postgres.fields import ArrayField


class SimObject(models.Model):

    class Meta:
        abstract = True

    name = models.CharField(max_length=128)
    description = models.CharField(max_length=255)


class Simulation(SimObject):
    num_steps = models.PositiveIntegerField(default=1)


class UnitType(models.Model):

    class Meta:
        unique_together = ('sim', 'value')

    sim = models.ForeignKey(Simulation, on_delete=models.CASCADE)
    value = models.CharField(max_length=30)


class Attribute(models.Model):

    class Meta:
        unique_together = ('sim', 'value')

    sim = models.ForeignKey(Simulation, on_delete=models.CASCADE)
    value = models.CharField(max_length=30)


class Output(SimObject):
    sim = models.ForeignKey(Simulation, on_delete=models.CASCADE)
    unit_type = models.ForeignKey(UnitType, on_delete=models.PROTECT)


class Entity(SimObject):
    sim = models.ForeignKey(Simulation, on_delete=models.CASCADE)
    attributes = ArrayField(models.CharField(max_length=30))
    parent = models.ForeignKey('self', null=True, on_delete=models.CASCADE)
    is_source = models.BooleanField(default=False)


class Connector(SimObject):

    class Meta(SimObject.Meta):
        abstract = True

    unit_type = models.ForeignKey(UnitType, on_delete=models.PROTECT)
    parent = models.ForeignKey(Entity, on_delete=models.CASCADE)


class OutputConnector(Connector):
    copy_write = models.BooleanField(default=False)


class InputConnector(Connector):
    source = models.ForeignKey(
        OutputConnector, null=True, on_delete=models.SET_NULL)
    additive_write = models.BooleanField(default=False)


class SimOutputConnector(SimObject):
    source = models.ForeignKey(
        OutputConnector, null=True, on_delete=models.SET_NULL)
    additive_write = models.BooleanField(default=False)
    unit_type = models.ForeignKey(UnitType, on_delete=models.PROTECT)
    parent = models.ForeignKey(Output, on_delete=models.CASCADE)


class Endpoint(models.Model):
    parent = models.ForeignKey(OutputConnector, on_delete=models.CASCADE)
    bias = models.FloatField(default=0.0)
    input = models.ForeignKey(InputConnector, null=True, on_delete=models.CASCADE)
    sim_output = models.ForeignKey(SimOutputConnector, null=True, on_delete=models.CASCADE)


class Process(SimObject):
    parent = models.ForeignKey(Entity, on_delete=models.CASCADE)
    priority = models.PositiveSmallIntegerField(default=0)
    process_class = models.CharField(max_length=128)


class ProcessProperty(SimObject):

    BOOL_TYPE = 1
    NUMBER_TYPE = 2
    INT_TYPE = 3

    PROP_TYPE = (
        (BOOL_TYPE, 'boolean'),
        (NUMBER_TYPE, 'number'),
        (INT_TYPE, 'integer')
    )

    process = models.ForeignKey(Process, on_delete=models.CASCADE)
    property_type = models.PositiveIntegerField(
        choices=PROP_TYPE, default=NUMBER_TYPE)
    default_value = models.FloatField(default=0.0)
    max_value = models.FloatField(null=True)
    min_value = models.FloatField(null=True)
    property_value = models.FloatField()
