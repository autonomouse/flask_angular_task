#!/usr/bin/env python3
import os
import sys
import imp
import argparse

from migrate.versioning import api
from subprocess import check_call, check_output
from migrate.versioning import api

from app import app, db
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command")
    parser.add_argument('extra', nargs='*')
    args = parser.parse_args()

    args_list = []
    args_dict = {}
    for arg in args.extra:
        if '=' in arg:
            key, value = arg.split('=')
            args_dict[key] = value
        else:
            args_list.append(arg)
    private_methods = TaskBase().getAvailableMethods()
    tasks = Tasks()
    public_methods = tasks.getAvailableMethods()
    available_methods = [
        method for method in public_methods if method not in private_methods]
    try:
        return getattr(tasks, args.command)(*args_list, **args_dict)
    except AttributeError:
        print("There is no '" + args.command + "' command.")
        print("Available commands: \n * " + "\n * ".join(available_methods))


class TaskBase():
    """Helper methods, not meant to be called from the cli. """

    def getAvailableMethods(self):
        return [func for func in dir(self) if callable(getattr(self, func))
                and not func.startswith("__")]

    def sudo(self, cmd):
        sudo_cmd = ["sudo"]
        sudo_cmd.extend(cmd)
        return check_output(sudo_cmd)

    def db_create(self):
        """ https://blog.miguelgrinberg.com/post/
            the-flask-mega-tutorial-part-iv-database
        """

        db.create_all()
        if not os.path.exists(SQLALCHEMY_MIGRATE_REPO):
            api.create(SQLALCHEMY_MIGRATE_REPO, 'database repository')
            api.version_control(
                SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
        else:
            api.version_control(
                SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO,
                api.version(SQLALCHEMY_MIGRATE_REPO))
        print("Database created.")

    def db_migrate(self):
        """ https://blog.miguelgrinberg.com/post/
            the-flask-mega-tutorial-part-iv-database
        """

        v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
        migration = SQLALCHEMY_MIGRATE_REPO + (
            '/versions/%03d_migration.py' % (v+1))
        tmp_module = imp.new_module('old_model')
        old_model = api.create_model(
            SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
        exec(old_model, tmp_module.__dict__)
        script = api.make_update_script_for_model(
            SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, tmp_module.meta,
            db.metadata)
        open(migration, "wt").write(script)
        api.upgrade(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
        v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
        print('New migration saved as ' + migration)
        print('Current database version: ' + str(v))

    def db_upgrade(self):
        """ https://blog.miguelgrinberg.com/post/
            the-flask-mega-tutorial-part-iv-database
        """

        api.upgrade(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
        v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
        print('Current database version: ' + str(v))

    def db_downgrade(self):
        """ https://blog.miguelgrinberg.com/post/
            the-flask-mega-tutorial-part-iv-database
        """

        v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
        api.downgrade(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, v - 1)
        v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
        print('Current database version: ' + str(v))


class Tasks(TaskBase):
    """Tasks meant to be callable from the cli. """

    def run(self):
        """ Run flask server. """
        app.run(debug=True)

    def db(self, action):
        """ Database actions. """

        switch = {
            "create": self.db_create,
            "migrate": self.db_migrate,
            "upgrade": self.db_upgrade,
            "downgrade": self.db_downgrade,
        }
        if action not in switch.keys():
            msg = "'{}' is not a recognised db action. Actions are: {}"
            raise Exception(msg.format(action, ", ".join(switch.keys())))
        switch.get(action)()


if __name__ == "__main__":
    sys.exit(main())
