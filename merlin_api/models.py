from django.db import models

class Simulation(models.Model):
    name = models.CharField(max_length=30)
    num_steps = models.IntegerField(default=1)


class UnitType(models.Model):
    sim = models.ForeignKey(Simulation, on_delete=models.CASCADE)
    value = models.CharField(max_length=30, unique=True)


class Attribute(models.Model):
    sim = models.ForeignKey(Simulation, on_delete=models.CASCADE)
    value = models.CharField(max_length=30, unique=True)
