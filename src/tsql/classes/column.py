import json

from .top_level import Menu
from .functions import get_name, rename


class ColumnMenu:
    rename = '[r] Rename Column'
    delete = '[d] Delete Column'
    data_type = '[t] Change Data Type'
    toggle = '[e] Edit Toggled Data'
    references = '[f] Toggle Referenced Column'
    collate = '[c] Change Collate Func'
    options = [
        rename,
        delete,
        data_type,
        toggle,
        collate,
        references
    ]
COLUMN = ColumnMenu()


class TogglesMenu:
    not_null = '[n] not_null'
    primary_key = '[p] primary_key'
    autoincrement = '[a] autoincrement'
    returns = '[r] returns'
    unique = '[u] unique'
    default = '[d] default'
    check = '[c] check'
    hidden = '[h] hidden'
    options = [
        not_null,
        primary_key,
        autoincrement,
        returns,
        unique,
        default,
        check,
        #hidden
    ]
TOGGLES = TogglesMenu()


class ColumnToggles(Menu):
    def __init__(self, column):
        self.column = column
        super().__init__(blueprint=TOGGLES)
                

    def select(self, option):
         match option:
            case None:
                self.active = False
            case TOGGLES.not_null:
                self.column.not_null = not self.column.not_null
            case TOGGLES.unique:
                self.column.unique = not self.column.unique
            case TOGGLES.returns:
                self.column.returns = not self.column.returns
            case TOGGLES.autoincrement:
                self.column.autoincrement = not self.column.autoincrement
            case TOGGLES.hidden:
                self.column.hidden = not self.column.hidden

            case TOGGLES.primary_key:
                if not self.column.primary_key:
                    for column in self.column.table.columns:
                        if column.primary_key:
                            column.primary_key = False
                    self.column.primary_key = True
                    return None

                self.column.primary_key = False

            case TOGGLES.default:
                if self.column.data_type == 'BLOB':
                    print('\nDefault value on blob type column is not supported')
                    return None
                 
                if not self.column.default:
                    self.column.default = self.get_default_value()
                    if self.column.default:
                        self.not_null = True
                    return None

                self.not_null = False
                self.column.default = None

            case TOGGLES.check:
                if self.column.check:
                    self.column.check = False
                    return None

                res = input('\nEnter the CHECK condition\n(checks are not validated, use at your own risk)\n')
                if res:
                    self.column.check = res


    def new_cycle(self):
        self.column.new_cycle()


    def get_default_value(self):
        valid = False
        while not valid:
            default = input('\nEnter the default column value:\n')
            if (
                default == 'CURRENT_TIME' 
                or default == 'CURRENT_TIME'
                or default == 'CURRENT_TIMESTAMP'
            ):
                return default

            try:
                match self.column.data_type:
                    case 'TEXT':
                        return f"'{default}'"
                    case 'INTEGER':
                        return int(default)
                    case 'REAL':
                        return float(default)

            except ValueError:
                print(f'Invalid entry for data type {self.column.data_type}')


class Column(Menu):
    def __init__(self, table, load=None):
        self.table = table

        if not load:
            get_name(self) 
            self.data_type = 'TEXT'
            self.py_data_type = 'str'
            self.not_null = True
            self.primary_key = False
            self.autoincrement = False
            self.returns = True
            self.unique = False
            self.default = None
            self.check = None
            self.check_conditions = []
            self.collate = 'BINARY'
            self.hidden = False
            self.references = False
            self.referenced_column = None
        else:
            self.config = load

        super().__init__(blueprint=COLUMN)


    def select(self, option):
        match option:
            case COLUMN.toggle:
                toggle_menu = ColumnToggles(self)
                toggle_menu.enter()

            case COLUMN.rename:
                rename(self)

            case COLUMN.data_type:
                data_type_selector = Menu(
                    options=[
                        '[1] TEXT',
                        '[2] INTEGER',
                        '[3] REAL',
                        '[4] BLOB'
                    ]
                )
                res = data_type_selector.enter_once()
                match res:
                    case '[1] TEXT':
                        self.data_type = 'TEXT'
                        self.py_data_type = 'str'
                    case '[2] INTEGER':
                        self.data_type = 'INTEGER'
                        self.py_data_type = 'int'
                    case '[3] REAL':
                        self.data_type = 'REAL'
                        self.py_data_type = 'float'
                    case '[4] BLOB':
                        self.data_type = 'BLOB'
                        self.py_data_type = 'bytes'

            case COLUMN.references:
                if not self.references:
                    tables = [
                        table.name for table in self.table.database.tables
                    ]
                    table_selector = Menu(
                        options=tables,
                        title='Select Table to Reference:'
                    )
                    res = table_selector.enter_once()
                    table = [
                        table for table in self.table.database.tables
                        if table.name == res
                    ][0]

                    columns = [column.name for column in table.columns]
                    column_selector = Menu(
                        options=columns,
                        title='Select Column to Reference:'
                    )
                    res = column_selector.enter_once()
                    column = [
                        column for column in table.columns
                        if column.name == res
                    ][0]
                    self.references = True
                    self.referenced_column = column

                else:
                    self.references = False
                    self.referenced_column = None

            case COLUMN.collate:
                if not self.data_type == 'TEXT':
                    print('\ncollate settings only apply to TEXT columns\n')
                    return None

                collate = Menu(
                    options=[
                        'BINARY',
                        'NOCASE',
                        'RTRIM'
                    ]
                ).enter_once()

                if not collate:
                    return None

                self.collate = collate

            case COLUMN.delete:
                self.table.delete_child(self)
                self.active = False


    def new_cycle(self):
        conf = self.config
        if self.data_type != 'TEXT' or self.collate == 'BINARY':
            del conf['collate']
        print(
            '\nCOLUMN:',
            json.dumps(
                {
                    key: value for key, value in conf.items()
                    if value
                },
                indent=4
            )
        )


    @property
    def __name__(self):
        return 'Column'


    @property
    def config(self):
        col_dict = {
            'name': self.name,
            'data_type': self.data_type,
            'not_null': self.not_null,
            'primary_key': self.primary_key,
            'autoincrement': self.autoincrement,
            'returns': self.returns,
            'unique': self.unique,
            'default': self.default,
            'check': self.check,
            'collate': self.collate,
            'hidden': self.hidden,
            'references': False
        }
        if self.references:
            col_dict['references'] = True
            col_dict['referenced_table'] = self.referenced_column.table.name
            col_dict['referenced_column'] = self.referenced_column.name
        return col_dict


    @config.setter
    def config(self, config_dict):
        self.name = config_dict['name']
        self.data_type = config_dict['data_type']
        self.not_null = config_dict['not_null']
        self.primary_key = config_dict['primary_key']
        self.autoincrement = config_dict['autoincrement']
        self.returns = config_dict['returns']
        self.unique = config_dict['unique']
        self.check = config_dict['check']
        self.collate = config_dict['collate']
        self.hidden = config_dict['hidden']

        self.references = config_dict['references']
        if self.references:
            table = [
                table for table in self.table.database.tables
                if table.name == config_dict['referenced_table']
            ][0]
            self.referenced_column = [
                column for column in table.columns
                if column.name == config_dict['referenced_column']
            ][0]

        match self.data_type:
            case 'TEXT':
                self.py_data_type = 'str'
            case 'INTEGER':
                self.py_data_type = 'int'
            case 'REAL':
                self.py_data_type = 'float'
            case 'BLOB':
                self.py_data_type = 'bytes'

        if config_dict['default']:
            match self.data_type:
                case 'TEXT':
                    self.default = config_dict['default']
                case 'INTEGER':
                    self.default = int(config_dict['default'])
                case 'REAL':
                    self.default = float(config_dict['default'])
                case False:
                    self.default = None
        else:
            self.default = None


    def validate_name(self, name):
        if name in [
            obj.name for obj in self.table.children
        ]:
            print('Column name must be unique to all table children')
            return False
        return True

