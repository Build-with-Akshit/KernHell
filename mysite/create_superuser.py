import os
import django
from django.contrib.auth import get_user_model

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings.dev")
django.setup()

User = get_user_model()
username = "admin"
password = "admin"
email = "admin@example.com"

if not User.objects.filter(username=username).exists():
    print(f"Creating superuser: {username}")
    User.objects.create_superuser(username, email, password)
    print("✅ Superuser created successfully.")
else:
    print(f"ℹ️ Superuser '{username}' already exists.")
