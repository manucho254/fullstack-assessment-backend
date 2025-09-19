# Ensure pip is available
python3 -m ensurepip --upgrade || true

# Install Python dependencies
pip3 install -r requirements.txt

# Run Django migrations and collect static files
python3 manage.py makemigrations
python3 manage.py migrate

# Load services from JSON file
python3 manage.py load_services

python3 manage.py collectstatic --noinput

# Create Superuser if it doesn't exist
python3 manage.py shell -c "
from django.contrib.auth.models import User;
import os;
username = os.getenv('SUPERUSER_USERNAME', 'admin');
email = os.getenv('SUPERUSER_EMAIL', 'admin@test.com');
password = os.getenv('SUPERUSER_PASSWORD', 'testing200');
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password);
else:
    print('Superuser already exists');
"