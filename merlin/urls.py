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
router.register(r'simulation', views.SimulationViewSet)
router.register(r'unittype', views.UnitTypeViewSet)
router.register(r'attribute', views.AttributeViewSet)
router.register(r'output', views.OutputViewSet)
router.register(r'entity', views.EntityViewSet)
router.register(r'outputconnector', views.OutputConnectorViewSet)
router.register(r'inputconnector', views.InputConnectorViewSet)
router.register(r'simoutputconnector', views.SimOutputConnectorViewSet)
router.register(r'endpoint', views.EndpointViewSet)
router.register(r'process', views.ProcessViewSet)
router.register(r'processproperty', views.ProcessPropertyViewSet)
router.register(r'simulation-run', views.SimulationRunViewSet, base_name='simulation-run')

urlpatterns = [
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include(
        'rest_framework.urls', namespace='rest_framework'))
]
