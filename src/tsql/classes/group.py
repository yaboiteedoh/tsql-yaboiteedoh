import json

from .top_level import Menu
from .functions import get_name, rename


class GroupMenu:
    rename = '[r] Rename Group'
    delete = '[d] Delete Group'
    edit = '[e] Edit Columns'
    options = [
        rename,
        delete,
        edit
    ]
GROUP = GroupMenu()


class Group(Menu):
    def __init__(self, table, load=None):
        self.table = table
        self.columns = []

        if not load:
            get_name(self)
        else:
            self.config = load

        super().__init__(blueprint=GROUP)


    def select(self, option):
        match option:
            case GROUP.rename:
                rename(self)

            case GROUP.delete:
                self.table.delete_child(self.name)
                self.active = False

            case GROUP.edit:
                selector = Menu(
                    options=[column.name for column in self.table.columns],
                    multi_select=True
                )

                res = selector.enter_once()
                if res is None:
                    return

                self.columns = [
                    column for column in self.table.columns
                    if column.name in res
                ]
                self.py_data_type = self.columns[0].py_data_type


    def new_cycle(self):
        print('\nGROUP:', json.dumps(self.config, indent=4))


    @property
    def __name__(self):
        return 'Group'

    
    @property
    def config(self):
        return {
            'name': self.name,
            'columns': [column.name for column in self.columns]
        }


    @config.setter
    def config(self, config_dict):
        columns = config_dict['columns']

        self.name = config_dict['name']
        self.columns = [
            column for column in self.table.columns
            if column.name in columns
        ]
        if self.columns:
            self.py_data_type = self.columns[0].py_data_type


    def validate_name(self, name):
        if name in [
            obj.name for obj in self.table.children
        ]:
            print('Group name must be unique to all table children')
            return False
        return True

