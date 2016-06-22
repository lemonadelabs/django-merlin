from django.db import models
from django.contrib.postgres.fields import ArrayField, JSONField
import datetime


class SimObject(models.Model):

    class Meta:
        abstract = True

    name = models.CharField(max_length=128, default="", null=True)
    description = models.CharField(max_length=255, default="", null=True)


class Simulation(SimObject):
    num_steps = models.PositiveIntegerField(default=1)
    start_date = models.DateField(default=datetime.datetime(2016, 7, 1))


class UnitType(models.Model):

    class Meta:
        unique_together = ('sim', 'value')

    sim = models.ForeignKey(
        Simulation, on_delete=models.CASCADE, related_name='unittypes')
    value = models.CharField(max_length=30)


class Attribute(models.Model):

    class Meta:
        unique_together = ('sim', 'value')

    sim = models.ForeignKey(
        Simulation, on_delete=models.CASCADE, related_name='attributes')
    value = models.CharField(max_length=30)


class Output(SimObject):
    sim = models.ForeignKey(
        Simulation, on_delete=models.CASCADE, related_name='outputs')
    attributes = ArrayField(models.CharField(max_length=128), default=[])
    unit_type = models.ForeignKey(UnitType, on_delete=models.PROTECT)
    minimum = models.FloatField(null=True)
    deliver_date = models.DateField(null=True)
    display_pos_x = models.FloatField(null=True)
    display_pos_y = models.FloatField(null=True)

    def __str__(self):
        return """
        <Output: {0}
            id: {5}
            sim: {1}
            unit_type: {2}
            minimum: {6}
            display_pos_x: {3}
            display_pos_y: {4}
        """.format(
                id(self),
                self.sim,
                self.unit_type,
                self.display_pos_x,
                self.display_pos_y,
                self.id,
                self.minimum)


class Entity(SimObject):
    sim = models.ForeignKey(
        Simulation, on_delete=models.CASCADE, related_name='entities')
    attributes = ArrayField(models.CharField(max_length=128))
    parent = models.ForeignKey(
        'self', null=True, on_delete=models.CASCADE, related_name='children')
    is_source = models.BooleanField(default=False)
    display_pos_x = models.FloatField(null=True)
    display_pos_y = models.FloatField(null=True)


class Connector(SimObject):

    class Meta(SimObject.Meta):
        abstract = True
    unit_type = models.ForeignKey(UnitType, on_delete=models.PROTECT)


class OutputConnector(Connector):

    COPY_WRITE = 1
    WEIGHTED = 2
    ABSOLUTE = 3

    APPORTION_RULE = (
        (COPY_WRITE, 'copy_write'),
        (WEIGHTED, 'weighted'),
        (ABSOLUTE, 'absolute')
    )

    parent = models.ForeignKey(
        Entity, on_delete=models.CASCADE, related_name='outputs')
    apportion_rule = models.PositiveIntegerField(
        choices=APPORTION_RULE, default=WEIGHTED)

    def __str__(self):
        return """
        <Output: {0}
            id: {1}
            name: {5}
            unit_type: {2}
            parent: {3}
            apportion: {4}
        """.format(
            id(self),
            self.id,
            self.unit_type.value,
            self.parent,
            self.apportion_rule,
            self.name)


class InputConnector(Connector):
    source = models.ForeignKey(
        OutputConnector, null=True, on_delete=models.SET_NULL)
    additive_write = models.BooleanField(default=False)
    parent = models.ForeignKey(
        Entity, on_delete=models.CASCADE, related_name='inputs')

    def __str__(self):
        return """
        <Input: {0}
            id: {1}
            name: {5}
            unit_type: {2}
            parent: {3}
            source: {4}
        """.format(
            id(self),
            self.id,
            self.unit_type.value,
            self.parent,
            self.source,
            self.name)


class SimOutputConnector(SimObject):
    source = models.ForeignKey(
        OutputConnector, null=True, on_delete=models.SET_NULL)
    additive_write = models.BooleanField(default=False)
    unit_type = models.ForeignKey(UnitType, on_delete=models.PROTECT)
    parent = models.ForeignKey(
        Output, on_delete=models.CASCADE, related_name='inputs')

    def __str__(self):
        return """
        <SimOutputConnector: {0}
            id: {1}
            name: {5}
            unit_type: {2}
            parent: {3}
            source: {4}
        """.format(
            id(self),
            self.id,
            self.unit_type.value,
            self.parent,
            self.source,
            self.name)


class Endpoint(SimObject):
    parent = models.ForeignKey(
        OutputConnector, on_delete=models.CASCADE, related_name='endpoints')
    bias = models.FloatField(default=0.0)
    input = models.ForeignKey(
        InputConnector, null=True, on_delete=models.CASCADE)
    sim_output = models.ForeignKey(
        SimOutputConnector, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return """
        <model.Endpoint: {0}>
            id: {5}
            parent: {1}
            bias: {2}
            input: {3}
            sim_output: {4}""".format(
                id(self),
                self.parent,
                self.bias,
                self.input,
                self.sim_output,
                self.id)


class Process(SimObject):
    parent = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='processes')
    priority = models.PositiveSmallIntegerField(default=100)
    process_class = models.CharField(max_length=256)
    parameters = JSONField(default=dict())


class ProcessProperty(SimObject):

    BOOL_TYPE = 1
    NUMBER_TYPE = 2
    INT_TYPE = 3

    PROP_TYPE = (
        (BOOL_TYPE, 'boolean'),
        (NUMBER_TYPE, 'number'),
        (INT_TYPE, 'integer')
    )

    process = models.ForeignKey(
        Process, on_delete=models.CASCADE, related_name='properties')
    property_type = models.PositiveIntegerField(
        choices=PROP_TYPE, default=NUMBER_TYPE)
    default_value = models.FloatField(default=0.0)
    max_value = models.FloatField(null=True)
    min_value = models.FloatField(null=True)
    readonly = models.BooleanField(default=False)
    property_value = models.FloatField()



class Scenario(SimObject):
    sim = models.ForeignKey(
        Simulation,
        on_delete=models.CASCADE,
        related_name='scenarios')
    start_offset = models.PositiveIntegerField(null=True)


class Event(SimObject):
    scenario = models.ForeignKey(
        Scenario,
        on_delete=models.CASCADE,
        related_name='events')
    time = models.PositiveIntegerField(default=1)
    actions = JSONField(default=list())


class Project(SimObject):

    priority = models.PositiveIntegerField(default=1)
    type = models.CharField(max_length=128, default="", null=True)
    is_ringfenced = models.BooleanField(default=False)
    achievability = models.IntegerField(default=0)
    attractiveness = models.IntegerField(default=0)
    dependencies = models.ManyToManyField(
        'self',
        related_name='required_by',
        symmetrical=False,
        default=None)


class ProjectPhase(SimObject):

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='phases', null=True)
    scenario = models.ForeignKey(
        Scenario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='project_phases')
    investment_cost = models.IntegerField(default=0)
    service_cost = models.IntegerField(default=0)
    start_date = models.DateField(default=datetime.datetime(2016, 1, 1))
    end_date = models.DateField(default=datetime.datetime(2016, 4, 1))
    is_active = models.BooleanField(default=True)
    capitalization = models.FloatField(default=0.0)
