import json

from .top_level import Menu
from .functions import get_name, rename, pascal_case
from .column import Column
from .filter import Filter
from .group import Group


ROWID = {
    'name': 'rowid',
    'data_type': 'INT',
    'not_null': False,
    'primary_key': True,
    'autoincrement': True,
    'returns': True,
    'unique': True,
    'default': None,
    'check': None,
    'collate': 'BINARY',
    'hidden': False,
    'references': False
}


class TableMenu:
    details = '[t] Show Table Details'
    new = '[n] New Column/Filter/Group'
    rename = '[r] Rename Table'
    delete = '[d] Delete Table'
    options = [
        details,
        new,
        rename,
        delete
    ]
TABLE = TableMenu()


class ViewSelectorMenu:
    columns = '[c] View Columns'
    groups = '[g] View Groups'
    filters = '[f] View Filters'
    all = '[a] View All'
VIEW_SELECTOR = ViewSelectorMenu()


class New:
    column = '[c] New Column'
    group = '[g] New Group'
    filter = '[f] New Filter'
    options = [
        column,
        group,
        filter
    ]
NEW = New()


class Table(Menu):
    def __init__(self, database, load=None):
        self.database = database
        self.children = []

        if not load:
            get_name(self)
            self.dataclass = pascal_case(self.name[:-1])
            rowid = Column(self, load=ROWID)
            self.children.append(rowid)
        else:
            self.config = load

        super().__init__(blueprint=TABLE)


    def select(self, option):
        match option:
            case TABLE.details:
                views = []
                if self.columns:
                    views.append(VIEW_SELECTOR.columns)
                if self.groups:
                    views.append(VIEW_SELECTOR.groups)
                if self.filters:
                    views.append(VIEW_SELECTOR.filters)
                if not views:
                    print('Table is currently empty')
                    return
                views.append(VIEW_SELECTOR.all)

                view_selector = Menu(options=views, title='Select a category:')
                res = view_selector.enter_once()
                
                if res is None:
                    return

                match res:
                    case VIEW_SELECTOR.columns:
                        objects = self.columns
                    case VIEW_SELECTOR.groups:
                        objects = self.groups
                    case VIEW_SELECTOR.filters:
                        objects = self.filters
                    case VIEW_SELECTOR.all:
                        objects = self.children

                names = [obj.name for obj in objects]

                object_selector = Menu(
                    options=names,
                    title='Select to Inspect:'
                )
                res = object_selector.enter_once()

                if res is None:
                    return

                selection = [x for x in objects if x.name == res][0]
                selection.enter()


            case TABLE.delete:
                self.database.delete_table(self)
                self.active = False

            case TABLE.new:
                selector = Menu(blueprint=NEW)
                selection = selector.enter_once()

                match selection:
                    case NEW.column:
                        child = Column(self)
                    case NEW.filter:
                        child = Filter(self)
                    case NEW.group:
                        child = Group(self)
                    case None:
                        return

                self.children.append(child)
                child.enter()


            case TABLE.rename:
                rename(self)
                self.dataclass = pascal_case(self.name[:-1])
            

    def new_cycle(self):
        print(
            '\nTABLE:',
            json.dumps(
                {
                    'name': self.name,
                    'columns': len(self.columns),
                    'groups': len(self.groups),
                    'filters': len(self.filters)
                },
                indent=4
            )
        )


    @property
    def __name__(self):
        return 'Table'


    @property
    def config(self):
        return {
            'name': self.name,
            'columns': [column.config for column in self.columns],
            'groups': [group.config for group in self.groups],
            'filters': [filter.config for filter in self.filters]
        }


    @config.setter
    def config(self, config_dict):
        columns = config_dict['columns']
        groups = config_dict['groups']
        filters = config_dict['filters']

        self.name = config_dict['name']
        self.dataclass = pascal_case(self.name[:-1])
        for column in columns:
            c = Column(self, load=column)
            self.children.append(c)
        for group in groups:
            g = Group(self, load=group)
            self.children.append(g)
        for filter in filters:
            f = Filter(self, load=filter)
            self.children.append(f)


    def validate_name(self, name):
        if name in [
            table.name for table in self.database.tables
        ]:
            print('Table name must be unique to Database\n')
            return False
        return True


    @property
    def columns(self):
        return [child for child in self.children if child.__name__ == 'Column']


    @property
    def groups(self):
        return [child for child in self.children if child.__name__ == 'Group']


    @property
    def filters(self):
        return [child for child in self.children if child.__name__ == 'Filter']


    def delete_child(self, child):
        children.remove(child)
        self.database.clear_references(child)

