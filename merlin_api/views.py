from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from . import pymerlin_adapter
from .serializers import *
from .models import *


class SimulationRunViewSet(viewsets.GenericViewSet):
    """
    Runs a merlin simulation and returns the telemetry result.
    """
    queryset = Simulation.objects.prefetch_related("entities", "outputs",
                                                 "outputs__inputs",
                                                 "unittypes", "attributes",
                                                 "entities__parent",
                                                 "entities__children",
                                                 "entities__outputs",
                                                 "entities__outputs__unit_type",
                                                 "entities__outputs__endpoints",
                                                 "entities__outputs__endpoints__input",
                                                 "entities__outputs__endpoints__sim_output",
                                                 "entities__inputs",
                                                 "entities__inputs__unit_type",
                                                 "entities__inputs__source",
                                                 "entities__processes",
                                                 "entities__processes__properties",
                                                 )
    serializer_class = SimulationSerializer

    def retrieve(self, request, pk=None):

        # parse steps arg
        steps_arg = request.query_params.get('steps', -1)
        try:
            steps_arg = int(steps_arg)
        except ValueError:
            steps_arg = -1

        scenarios = list()

        # parse scenario tag
        scenario_arg = request.query_params.get('scenarios', 'none')
        if scenario_arg == 'all':
            scenarios = Scenario.objects.all()

        # parse scenario filters
        i = 0
        k = 's' + str(i)
        while k in request.query_params:
            s_id = request.query_params[k]
            i += 1
            k = 's' + str(i)
            try:
                s_id = int(s_id)
                scenario = Scenario.objects.prefetch_related("events",
                                                             "sim",
                                                             ).get(pk=s_id)
                scenarios.append(scenario)
            except ValueError:
                continue

        sim = get_object_or_404(self.get_queryset(), pk=pk)

        result = pymerlin_adapter.run_simulation(
            sim,
            steps=steps_arg,
            scenarios=scenarios)
        return Response(result)


# Model view sets


class ProjectPhaseViewSet(viewsets.ModelViewSet):
    queryset = ProjectPhase.objects.all()
    serializer_class = ProjectPhaseSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventsSerializer


class ScenarioViewSet(viewsets.ModelViewSet):
    queryset = Scenario.objects.all()
    serializer_class = ScenarioSerializer


class SimulationViewSet(viewsets.ModelViewSet):
    queryset = Simulation.objects.all()
    serializer_class = SimulationSerializer


class UnitTypeViewSet(viewsets.ModelViewSet):
    queryset = UnitType.objects.all()
    serializer_class = UnitTypeSerializer


class AttributeViewSet(viewsets.ModelViewSet):
    queryset = Attribute.objects.all()
    serializer_class = AttributeSerializer


class OutputViewSet(viewsets.ModelViewSet):
    queryset = Output.objects.all()
    serializer_class = OutputSerializer

    def get_queryset(self):
        queryset = self.queryset
        # parse attribute filters
        if 'a' in self.request.query_params:
            attrs = self.request.query_params.copy().pop('a')
            queryset = queryset.filter(attributes__contains=attrs)

        return queryset


class EntityViewSet(viewsets.ModelViewSet):
    queryset = Entity.objects.all()
    serializer_class = EntitySerializer

    def get_queryset(self):
        queryset = self.queryset
        # parse attribute filters
        if 'a' in self.request.query_params:
            attrs = self.request.query_params.copy().pop('a')
            queryset = queryset.filter(attributes__contains=attrs)

        return queryset


class OutputConnectorViewSet(viewsets.ModelViewSet):
    queryset = OutputConnector.objects.all()
    serializer_class = OutputConnectorSerializer


class InputConnectorViewSet(viewsets.ModelViewSet):
    queryset = InputConnector.objects.all()
    serializer_class = InputConnectorSerializer


class SimOutputConnectorViewSet(viewsets.ModelViewSet):
    queryset = SimOutputConnector.objects.all()
    serializer_class = SimOutputConnectorSerializer


class EndpointViewSet(viewsets.ModelViewSet):
    queryset = Endpoint.objects.all()
    serializer_class = EndpointSerializer


class ProcessViewSet(viewsets.ModelViewSet):
    queryset = Process.objects.all()
    serializer_class = ProcessSerializer


class ProcessPropertyViewSet(viewsets.ModelViewSet):
    queryset = ProcessProperty.objects.all()
    serializer_class = ProcessPropertySerializer
