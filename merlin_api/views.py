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
    queryset = Simulation.objects.all()
    serializer_class = SimulationSerializer

    def retrieve(self, request, pk=None):
        sim = get_object_or_404(self.get_queryset(), pk=pk)
        result = pymerlin_adapter.run_simulation(sim)
        return Response(result)


# Model view sets

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


class EntityViewSet(viewsets.ModelViewSet):
    queryset = Entity.objects.all()
    serializer_class = EntitySerializer


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
