import os
import sys


def main():
    """Run administrative tasks."""
    # Point Django to your settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            'available on your PYTHONPATH environment variable? Did you '
            'forget to activate a virtual environment?'
        ) from exc

    # Initialize Django settings
    # django.setup() # Usually called implicitly by execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
