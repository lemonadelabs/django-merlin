from django.db import models
from django.contrib.postgres.fields import ArrayField


class SimObject(models.Model):

    class Meta:
        abstract = True

    name = models.CharField(max_length=30)


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
    attributes = ArrayField(
        models.ForeignKey(Attribute, on_delete=models.PROTECT))
    parent = models.ForeignKey('self', on_delete=models.CASCADE)
