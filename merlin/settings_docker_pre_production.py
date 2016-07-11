from merlin.settings import *

# for pre-production
DEBUG = False
ALLOWED_HOSTS = ["localhost", "192.168.99.100"]
SECRET_KEY = 'sdakl aeorij23jfalkja adsfjjeoriewoiu2034982398409'

STATIC_ROOT = '/var/webstack-data/django-static'
STATIC_URL = '/django-static/'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME' : 'merlin',
        'USER' : 'postgres',
        'PASSWORD' : 'tuatara',
        'HOST' : 'the-postgres',
        'PORT' : '5432'
    }
}

