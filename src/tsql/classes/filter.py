import json

from .top_level import Menu
from .functions import get_name, rename


class FilterMenu:
    rename = '[r] Rename Filter'
    delete = '[d] Delete Filter'
    edit = '[e] Edit Queries'
    options = [
        rename,
        delete,
        edit
    ]
FILTER = FilterMenu()


class Filter(Menu):
    def __init__(self, table, load=None):
        self.table = table

        if not load:
            get_name(self)
            self.queries = []
        else:
            self.config = load

        super().__init__(blueprint=FILTER)


    def select(self, option):
        match option:
            case FILTER.rename:
                rename(self)

            case FILTER.delete:
                self.table.delete_child(self.name)
                self.active = False

            case FILTER.edit:
                options = self.table.columns + self.table.groups

                selector = Menu(
                    options=[option.name for option in options],
                    multi_select=True
                )

                res = selector.enter_once()
                if res is None:
                    return

                self.queries = [
                    option for option in options
                    if option.name in res
                ]


    def new_cycle(self):
        print('\nFILTER:', json.dumps(self.config, indent=4))


    @property
    def __name__(self):
        return 'Filter'


    @property
    def config(self):
        return {
            'name': self.name,
            'queries': [query.name for query in self.queries]
        }


    @config.setter
    def config(self, config_dict):
        options = self.table.columns + self.table.groups
        queries = config_dict['queries']

        self.name = config_dict['name']
        self.queries = [
            option for option in options
            if option.name in queries
        ]

