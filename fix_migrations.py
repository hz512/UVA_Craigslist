#!/usr/bin/python

import shutil
from os import remove, system
import sys

if __name__ == "__main__":
    if not ("--force" in sys.argv):
        print("WARNING: THIS WILL DELETE ALL CURRENT MIGRATIONS AND THE DATABASE.")
        input("PRESS ENTER TO CONTINUE.")

    print("\nDeleting all migrations and database...")
    try:
        shutil.rmtree("./main/migrations")
    except FileNotFoundError:
        pass
    try:
        shutil.rmtree("./users/migrations")
    except FileNotFoundError:
        pass
    try:
        remove("./db.sqlite3")
    except FileNotFoundError:
        pass

    print("\nRemigrating...")
    system("python manage.py makemigrations users")
    system("python manage.py makemigrations main")
    system("python manage.py makemigrations")
    system("python manage.py migrate")

    print("\nCreating superuser with username \"admin\" and password \"password\"")
    system("python manage.py shell -c \"from users.models import CustomUser; CustomUser.objects.create_superuser('admin', 'admin@admin.com', 'password')\"")
