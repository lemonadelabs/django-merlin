from rest_framework import viewsets
from .serializers import *
from .models import *

# class SimulationModelViewSet(viewsets.ViewSet):
#
#     def list(s=elf, request):
#         pass
#
#     def retrieve(self, request, pk=None):
#         pass


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
