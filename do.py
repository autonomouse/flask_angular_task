#!/usr/bin/env python3
import os
import sys
import imp
import argparse

from subprocess import check_call, check_output

from migrate.versioning import api
os.environ["APP_SETTINGS"] = "config.DevelopmentConfig"
from app import app, db


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
        method = getattr(tasks, args.command)
    except AttributeError:
        print("There is no '" + args.command + "' command.")
        print("Available commands: \n * " + "\n * ".join(available_methods))
    method(*args_list, **args_dict)


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
        if not os.path.exists(app.config['SQLALCHEMY_MIGRATE_REPO']):
            api.create(app.config['SQLALCHEMY_MIGRATE_REPO'],
                       'database repository')
            api.version_control(app.config['SQLALCHEMY_DATABASE_URI'],
                                app.config['SQLALCHEMY_MIGRATE_REPO'])
        else:
            api.version_control(
                app.config['SQLALCHEMY_DATABASE_URI'],
                app.config['SQLALCHEMY_MIGRATE_REPO'],
                api.version(app.config['SQLALCHEMY_MIGRATE_REPO']))
        print("Database created.")

    def db_migrate(self):
        """ https://blog.miguelgrinberg.com/post/
            the-flask-mega-tutorial-part-iv-database
        """

        v = api.db_version(app.config['SQLALCHEMY_DATABASE_URI'],
                           app.config['SQLALCHEMY_MIGRATE_REPO'])
        migration = app.config['SQLALCHEMY_MIGRATE_REPO'] + (
            '/versions/%03d_migration.py' % (v+1))
        tmp_module = imp.new_module('old_model')
        old_model = api.create_model(
            app.config['SQLALCHEMY_DATABASE_URI'],
            app.config['SQLALCHEMY_MIGRATE_REPO'])
        exec(old_model, tmp_module.__dict__)
        script = api.make_update_script_for_model(
            app.config['SQLALCHEMY_DATABASE_URI'],
            app.config['SQLALCHEMY_MIGRATE_REPO'],
            tmp_module.meta, db.metadata)
        open(migration, "wt").write(script)
        api.upgrade(app.config['SQLALCHEMY_DATABASE_URI'],
                    app.config['SQLALCHEMY_MIGRATE_REPO'])
        v = api.db_version(app.config['SQLALCHEMY_DATABASE_URI'],
                           app.config['SQLALCHEMY_MIGRATE_REPO'])
        print('New migration saved as ' + migration)
        print('Current database version: ' + str(v))

    def db_upgrade(self):
        """ https://blog.miguelgrinberg.com/post/
            the-flask-mega-tutorial-part-iv-database
        """

        api.upgrade(app.config['SQLALCHEMY_DATABASE_URI'],
                    app.config['SQLALCHEMY_MIGRATE_REPO'])
        v = api.db_version(app.config['SQLALCHEMY_DATABASE_URI'],
                           app.config['SQLALCHEMY_MIGRATE_REPO'])
        print('Current database version: ' + str(v))

    def db_downgrade(self):
        """ https://blog.miguelgrinberg.com/post/
            the-flask-mega-tutorial-part-iv-database
        """

        v = api.db_version(app.config['SQLALCHEMY_DATABASE_URI'],
                           app.config['SQLALCHEMY_MIGRATE_REPO'])
        api.downgrade(app.config['SQLALCHEMY_DATABASE_URI'],
                      app.config['SQLALCHEMY_MIGRATE_REPO'], v - 1)
        v = api.db_version(app.config['SQLALCHEMY_DATABASE_URI'],
                           app.config['SQLALCHEMY_MIGRATE_REPO'])
        print('Current database version: ' + str(v))

    def mkdir_p(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

    def install_deps(self):
        self.install_python_deps()
        self.install_js_deps()

    def install_python_deps(self):
        check_call([
            "pip3", "install", "--user", "flask-socketio", "flask-sqlalchemy",
            "sqlalchemy-migrate", "flask-wtf", "flask-restplus", "colour"])

    def install_js_deps(self):
        directory = app.config['STATIC_DIR']
        self.mkdir_p(directory)
        check_call([
            "npm", "install", "--prefix", directory, "angular@1.5.8",
            "jquery@3.1.1", "angular-route@1.5.8", "angular-resource@1.5.8",
            "bootstrap"])


class Tasks(TaskBase):
    """Tasks meant to be callable from the cli. """

    def run(self, debug_mode_on=True):
        """ Run flask server. """
        os.environ["FLASK_DEBUG"] = '1' if debug_mode_on else '0'
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

    def deps(self, action):
        """ Dependency actions. """

        switch = {
            "install": self.install_deps,
        }
        if action not in switch.keys():
            msg = "'{}' is not a recognised deps action. Actions are: {}"
            raise Exception(msg.format(action, ", ".join(switch.keys())))
        switch.get(action)()


if __name__ == "__main__":
    sys.exit(main())
