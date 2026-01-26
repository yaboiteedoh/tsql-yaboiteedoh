from pathlib import Path
import json
import os


import jinja2


templates = os.path.dirname(os.path.abspath(__file__)) + '/templates'
env = jinja2.Environment(loader=jinja2.FileSystemLoader(templates))
env.globals['enumerate'] = enumerate
env.globals['len'] = len


DATABASE = env.get_template('database.jinja')
CLASSES = env.get_template('classes.jinja')
TABLE = env.get_template('table.jinja')
TABLE_INIT = env.get_template('table_init.jinja')


class Templater:
    def __init__(self, cwd):
        self.cwd = cwd


    def export_module(self, db):
        self.generate_filesystem(db)

        with open(self.fs['init'], 'w') as f:
            f.write('from .database import Database')

        for table in db.tables:
            table_class = TABLE.render(table=table)

            with open(self.fs['tables'][table.name], 'w') as f:
                f.write(table_class)

        for template, location in {
            DATABASE: self.fs['database'],
            CLASSES: self.fs['classes'],
            TABLE_INIT: self.fs['tables']['init']
        }.items():
            rendered_template = template.render(database=db)
            with open(location, 'w') as f:
                f.write(rendered_template)

   
    def generate_filesystem(self, db):
        path = [self.cwd, db.name]
        self.fs = {
            'path': Path(*path).resolve(),
            'init': Path(*path, '__init__.py').resolve(),
            'database': Path(*path, 'database.py').resolve(),
            'config': Path(*path, f'{db.name}.tsql').resolve(),
            'db': Path(*path, 'data.db').resolve(),
            'classes': Path(*path, 'classes.py').resolve(),
            'tables': {
                'path': Path(*path, 'tables').resolve(),
                'init': Path(*path, 'tables', '__init__.py').resolve()
            }
        }

        for table in db.tables:
            self.fs['tables'][table.name] = Path(*path, 'tables', f'{table.name}.py').resolve()

        self.fs['path'].mkdir()
        self.fs['tables']['path'].mkdir()

        open(self.fs['db'], 'w').close()

        with open(self.fs['config'], 'w') as f:
            json.dump(db.config, f, indent=4)

