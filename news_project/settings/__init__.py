import os
from decouple import config

env = config('DJANGO_ENV', default='dev').lower()

if env == 'prod' or env == 'production':
    from .prod import *
else:
    from .dev import *
