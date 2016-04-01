from rest_framework import serializers
from .models import *


class SimulationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Simulation
        fields = ('description', 'name', 'num_steps')


class UnitTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UnitType
        fields = ('sim', 'value')


class AttributeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Attribute
        fields = ('sim', 'value')


class OutputSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Output
        fields = ('description', 'name', 'sim', 'unit_type')


class EntitySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Entity
        fields = ('description', 'name', 'attributes', 'parent', 'sim', 'is_source')


class OutputConnectorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OutputConnector
        fields = ('description', 'name', 'parent', 'unit_type', 'copy_write')


class InputConnectorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = InputConnector
        fields = (
            'description',
            'name',
            'parent',
            'unit_type',
            'additive_write')


class SimOutputConnectorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SimOutputConnector
        fields = (
            'description',
            'name',
            'parent',
            'unit_type',
            'additive_write')


class EndpointSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Endpoint
        fields = ('bias', 'input', 'parent', 'sim_output')


class ProcessSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Process
        fields = ('description', 'name', 'parent', 'priority', 'process_class')


class ProcessPropertySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ProcessProperty
        fields = (
            'description',
            'name',
            'default_value',
            'max_value',
            'min_value',
            'process',
            'property_type',
            'property_value')
