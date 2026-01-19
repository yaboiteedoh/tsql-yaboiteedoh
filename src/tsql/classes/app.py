import json
import os
import shutil
from pathlib import Path

from .top_level import Menu
from .database import Database


class AppMenu:
    new = '[n] New Database'
    load = '[o] Load Database'
    options = [
        new,
        load
    ]
APP = AppMenu()


class App(Menu):
    def __init__(self, cwd, templater):
        self.cwd = cwd
        self.templater = templater
        super().__init__(blueprint=APP)

    
    def select(self, option):
        match option:
            case APP.new:
                self.database = Database(self)
                self.database.enter()
            
            case APP.load:
                working_dir = Path(self.cwd)

                active = True
                while active:
                    objects = os.listdir(working_dir)
                    directories = []
                    configs = []

                    for obj in objects:
                        if Path(working_dir, obj).is_dir():
                            directories.append(obj)
                        else:
                            if obj.split('.')[-1] == 'tsql':
                                configs.append(obj)

                    path = Menu(
                        options=['[..]'] + directories + configs,
                        title=str(working_dir.resolve()
                        )
                    )

                    pick_path = path.enter_once()

                    match pick_path:
                        case None:
                            active = False

                        case '[..]':
                            working_dir = Path(working_dir.parent)

                        case _:
                            if Path(working_dir, pick_path).is_dir():
                                working_dir = Path(working_dir, pick_path)

                            else:
                                with open(
                                    Path(working_dir, pick_path),
                                    'r'
                                ) as f:
                                    data = json.load(f)
                                self.database = Database(self, load=data)
                                self.database.enter()
                                active = False


    def new_cycle(self):
        print('\nSQL Module Generator Home')


    def export(self):
        for table in self.database.tables:
            for filter in table.filters:
                if not filter.queries:
                    print(f'Empty filter {filter.name} detected in table {table.name}\naborting export')
                    return
            for group in table.groups:
                if not group.columns:
                    print(f'Empty group {group.name} detected in table {table.name}\naborting export')
                    return

        dir = os.listdir(self.templater.cwd)
        if self.database.name in dir:
            overwrite = Menu(
                options=['Yes', 'No'],
                title=f'{self.database.name} module exists in directory, Overwrite?'
            )
        if overwrite == 'Yes':
            shutil.rmtree(f'{self.templater.cwd}/{self.database.name}')
            print(f'\nExporting to {self.templater.cwd}/{self.database.name}/')
            self.templater.export_module(self.database)
            return

        i = 0
        while True:
            dir = os.listdir(self.templater.cwd)
            if not self.database.name in dir:
                break
            i += 1
            self.database.name = self.database.name.split('-')[0] + f'-{i}'

        print(f'\nExporting to {self.templater.cwd}/{self.database.name}/')
        self.templater.export_module(self.database)


