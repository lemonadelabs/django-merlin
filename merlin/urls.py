"""merlin URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf.urls import url, include
from rest_framework import routers
from merlin_api import views


router = routers.DefaultRouter()
router.register(r'simulations', views.SimulationViewSet)
router.register(r'unittypes', views.UnitTypeViewSet)
router.register(r'attributes', views.AttributeViewSet)
router.register(r'outputs', views.OutputViewSet)
router.register(r'entities', views.EntityViewSet)
router.register(r'outputconnectors', views.OutputConnectorViewSet)
router.register(r'inputconnectors', views.InputConnectorViewSet)
router.register(r'simoutputconnectors', views.SimOutputConnectorViewSet)
router.register(r'endpoints', views.EndpointViewSet)
router.register(r'processes', views.ProcessViewSet)
router.register(r'processproperties', views.ProcessPropertyViewSet)
router.register(r'scenarios', views.ScenarioViewSet)
router.register(
    r'simulation-run',
    views.SimulationRunViewSet,
    base_name='simulation-run')

urlpatterns = [
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include(
        'rest_framework.urls', namespace='rest_framework'))
]
