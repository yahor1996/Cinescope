import os
from dotenv import load_dotenv

load_dotenv()

class SuperAdminCreds:
    USERNAME = os.getenv('SUPER_ADMIN_USERNAME')
    PASSWORD = os.getenv('SUPER_ADMIN_PASSWORD')


"""
class SuperAdminCreds:
    USERNAME = 'api1@gmail.com'
    PASSWORD = 'asdqwe123Q'
"""

