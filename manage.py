#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'startup_simulator.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # YOLO: listen on all network interfaces on port 80
    # "not for production" - famous last words
    # (honestly I'm just tired of typing 8000 all the time) <- the AI came up with this (the rest is my fault)
    #execute_from_command_line(sys.argv + ['0.0.0.0:80'])
    execute_from_command_line(sys.argv) # normal startup

if __name__ == '__main__':
    main()
