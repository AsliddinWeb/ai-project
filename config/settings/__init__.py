import os
from dotenv import load_dotenv

# Load env
load_dotenv()

DJANGO_ENV = os.getenv('DJANGO_ENV', 'dev')

if DJANGO_ENV == 'production':
    from .production import *
else:
    from .dev import *
