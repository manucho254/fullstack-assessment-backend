# Ensure pip is available
python3 -m ensurepip --upgrade || true

# Install Python dependencies
pip3 install -r requirements.txt

# Run Django migrations and collect static files
python3 manage.py makemigrations
python3 manage.py migrate

python3 manage.py collectstatic --noinput

# Create Superuser if it doesn't exist
python3 manage.py shell -c "
from apps.users.models import User;
import os;
email = os.getenv('SUPERUSER_EMAIL', 'admin@test.com');
password = os.getenv('SUPERUSER_PASSWORD', 'testing200');
if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(email=email, password=password);
else:
    print('Superuser already exists');
"