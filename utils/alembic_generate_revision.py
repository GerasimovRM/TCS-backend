import subprocess
from sys import argv

subprocess.run(f'alembic revision --autogenerate -m "{argv[1]}"')