from rest_framework import serializers
from .models import *


class EventsSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Event
        fields = (
            'id',
            'scenario',
            'time',
            'actions'
        )


class ScenarioSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Scenario
        fields = (
            'id',
            'sim',
            'start_offset',
            'events'
        )

class UnitTypeRelatedField(serializers.RelatedField):

    def to_internal_value(self, data):
        pass

    def to_representation(self, value):
        return value.value


class EndpointSerializer(serializers.ModelSerializer):

    class Meta:
        model = Endpoint
        fields = ('bias', 'input', 'parent', 'sim_output')


class OutputConnectorSerializer(serializers.HyperlinkedModelSerializer):

    unit_type = UnitTypeRelatedField(read_only=True)
    endpoints = EndpointSerializer(many=True, read_only=True)

    class Meta:
        model = OutputConnector
        fields = (
            'id',
            'description',
            'name',
            'parent',
            'unit_type',
            'apportion_rule',
            'endpoints')


class InputConnectorSerializer(serializers.HyperlinkedModelSerializer):

    unit_type = UnitTypeRelatedField(read_only=True)

    class Meta:
        model = InputConnector
        fields = (
            'id',
            'description',
            'name',
            'parent',
            'unit_type',
            'additive_write')


class ProcessPropertySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ProcessProperty
        fields = (
            'id',
            'description',
            'name',
            'default_value',
            'max_value',
            'min_value',
            'process',
            'property_type',
            'property_value')


class ProcessSerializer(serializers.HyperlinkedModelSerializer):

    properties = ProcessPropertySerializer(many=True, read_only=True)

    class Meta:
        model = Process
        fields = (
            'id',
            'description',
            'name',
            'parent',
            'priority',
            'process_class',
            'properties')


class EntitySerializer(serializers.HyperlinkedModelSerializer):

    outputs = OutputConnectorSerializer(many=True, read_only=True)
    inputs = InputConnectorSerializer(many=True, read_only=True)
    processes = ProcessSerializer(many=True, read_only=True)

    class Meta:
        model = Entity
        fields = (
            'id',
            'description',
            'name',
            'attributes',
            'parent',
            'sim',
            'is_source',
            'children',
            'outputs',
            'inputs',
            'processes',
            'display_pos_x',
            'display_pos_y')


class UnitTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UnitType
        fields = ('sim', 'value')


class AttributeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Attribute
        fields = ('sim', 'value')


class OutputSerializer(serializers.HyperlinkedModelSerializer):

    unit_type = UnitTypeRelatedField(read_only=True)

    class Meta:
        model = Output
        fields = (
            'id',
            'description',
            'name',
            'sim',
            'unit_type',
            'target',
            'deliver_date',
            'display_pos_x',
            'display_pos_y')


class SimulationSerializer(serializers.HyperlinkedModelSerializer):

    unittypes = UnitTypeSerializer(many=True, read_only=True)
    attributes = AttributeSerializer(many=True, read_only=True)
    entities = EntitySerializer(many=True, read_only=True)
    outputs = OutputSerializer(many=True, read_only=True)
    scenarios = ScenarioSerializer(many=True, read_only=True)

    class Meta:
        model = Simulation
        fields = (
            'id',
            'description',
            'name',
            'num_steps',
            'start_date',
            'unittypes',
            'attributes',
            'entities',
            'outputs',
            'scenarios')


class SimOutputConnectorSerializer(serializers.HyperlinkedModelSerializer):

    unit_type = UnitTypeRelatedField(read_only=True)

    class Meta:
        model = SimOutputConnector
        fields = (
            'id',
            'description',
            'name',
            'parent',
            'unit_type',
            'additive_write')


