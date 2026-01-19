import json

from .top_level import Menu
from .functions import get_name, rename, get_file_name
from .table import Table


class DatabaseMenu:
    tables = '[t] List Tables'
    new = '[n] New Table'
    rename = '[r] Rename Database'
    save = '[s] Save Database'
    export = '[e] Export Database'
    options = [
        tables,
        new,
        rename,
        save,
        export
    ]
DB = DatabaseMenu()


class Database(Menu):
    def __init__(self, app, load=None):
        self.tables = []
        self.app = app

        if not load:
            get_name(self)
        else:
            self.config = load

        super().__init__(blueprint=DB)


    def select(self, option):
        match option:
            case DB.rename:
                rename(self)

            case DB.tables:
                if not self.tables:
                    print('No Tables to Inspect')
                    return

                tables_list = Menu(
                    options=[table.name for table in self.tables],
                    title='Select a table to inspect:'
                )

                res = tables_list.enter_once()
                if res is None:
                    return

                table = [
                    table for table in self.tables if table.name == res
                ][0]

                table.enter()

            case DB.new:
                table = Table(self)
                self.tables.append(table)
                table.enter()

            case DB.save:
                name = get_file_name(self.app.cwd, self.name, 'tsql')
                path = self.app.cwd + f'/{name}.tsql'
                print(f'Saving config data to {path}')
                with open(path, 'w') as f:
                    json.dump(self.config, f, indent=4)

            case DB.export:
                self.app.export()


    def new_cycle(self):
        print(
            '\nDB:',
            json.dumps(
                {
                    'name': self.name,
                    'tables': len(self.tables)
                },
                indent=4
            )
        )


    @property
    def __name__(self):
        return 'Database'


    @property
    def config(self):
        return {
            self.name: {
                'tables': [table.config for table in self.tables]
            }
        }


    @config.setter
    def config(self, config_dict):
        self.name = list(config_dict.keys())[0]
        tables = config_dict[self.name]['tables']
        for table in tables:
            t = Table(self, load=table)
            self.tables.append(t)


    @staticmethod
    def validate_name(name):
        return True


    def delete_table(self, table):
        self.tables.remove(table)
        self.clear_table_references(table)


    def clear_references(self, check_column):
        for table in self.tables:
            for column in table.columns:
                if column.references:
                    if column.referenced_column == check_column:
                        column.references = False
                        column.referenced_column = None


    def clear_table_references(self, check_table):
        for table in self.tables:
            for column in table.columns:
                if column.references:
                    if column.referenced_column.table == check_table:
                        column.references = False
                        column.referenced_column = None


