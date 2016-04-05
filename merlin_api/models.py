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

    sim = models.ForeignKey(Simulation, on_delete=models.CASCADE, related_name='unittypes')
    value = models.CharField(max_length=30)


class Attribute(models.Model):

    class Meta:
        unique_together = ('sim', 'value')

    sim = models.ForeignKey(Simulation, on_delete=models.CASCADE, related_name='attributes')
    value = models.CharField(max_length=30)


class Output(SimObject):
    sim = models.ForeignKey(Simulation, on_delete=models.CASCADE, related_name='outputs')
    unit_type = models.ForeignKey(UnitType, on_delete=models.PROTECT)
    display_pos_x = models.FloatField(null=True)
    display_pos_y = models.FloatField(null=True)


class Entity(SimObject):
    sim = models.ForeignKey(Simulation, on_delete=models.CASCADE, related_name='entities')
    attributes = ArrayField(models.CharField(max_length=30))
    parent = models.ForeignKey('self', null=True, on_delete=models.CASCADE, related_name='children')
    is_source = models.BooleanField(default=False)
    display_pos_x = models.FloatField(null=True)
    display_pos_y = models.FloatField(null=True)


class Connector(SimObject):

    class Meta(SimObject.Meta):
        abstract = True
    unit_type = models.ForeignKey(UnitType, on_delete=models.PROTECT)


class OutputConnector(Connector):
    copy_write = models.BooleanField(default=False)
    parent = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='outputs')


class InputConnector(Connector):
    source = models.ForeignKey(
        OutputConnector, null=True, on_delete=models.SET_NULL)
    additive_write = models.BooleanField(default=False)
    parent = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='inputs')


class SimOutputConnector(SimObject):
    source = models.ForeignKey(
        OutputConnector, null=True, on_delete=models.SET_NULL)
    additive_write = models.BooleanField(default=False)
    unit_type = models.ForeignKey(UnitType, on_delete=models.PROTECT)
    parent = models.ForeignKey(Output, on_delete=models.CASCADE, related_name='inputs')


class Endpoint(models.Model):
    parent = models.ForeignKey(OutputConnector, on_delete=models.CASCADE, related_name='endpoints')
    bias = models.FloatField(default=0.0)
    input = models.ForeignKey(InputConnector, null=True, on_delete=models.CASCADE)
    sim_output = models.ForeignKey(SimOutputConnector, null=True, on_delete=models.CASCADE)


class Process(SimObject):
    parent = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='processes')
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

    process = models.ForeignKey(Process, on_delete=models.CASCADE, related_name='properties')
    property_type = models.PositiveIntegerField(
        choices=PROP_TYPE, default=NUMBER_TYPE)
    default_value = models.FloatField(default=0.0)
    max_value = models.FloatField(null=True)
    min_value = models.FloatField(null=True)
    property_value = models.FloatField()
