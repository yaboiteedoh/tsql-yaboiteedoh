from simple_term_menu import TerminalMenu


class Menu:
    """
    Root Class for the TerminalMenu wrapper

    Creates a persistent menu object, to be utilized in one of two modes
        continuous
        one shot
    """
    def __init__(
        self,
        title: str=None,
        options: list=[],
        blueprint: list=[],
        multi_select: bool=False
    ):
        '''
        Initializes the menu

        Returns:
            None

        Parameters:
            title:
                The text displayed above the menu options
                Only present while the menu is open

            options:
                a list of strings to be displayed in the menu

            blueprint:
                a python object representing a preconstructed menu,
                with attributes which contain strings representing standardized
                options, as well as an 'options' attribute which contains a list
                of the options in the order they should be displayed

                ex:
                    class Prefab:
                        option1 = '[1] option'
                        option2 = '[2] option'
                        options = [option2, option1]

            multi_select:
                a flag for the menu to allow for multiple selections without
                refreshing

        '''
        self.title = title
        self.active = False
        self.options = options
        self.multi_select = multi_select
        if blueprint:
            self.options = self.options + blueprint.options


    def enter(self):
        '''
        If self.new_cycle has been overwritten, prints the result of the property
        function, then opens the menu in continuous mode
            Leave the menu by setting self.active to False
            Other options alter the data within the object then display the menu
                again, with updated options
            The selection is passed into self.select() to be processed by the
                child class

        Returns:
            None
        '''
        prev_selection = 0
        self.active = True
        
        while True:
            if not self.active:
                break

            options = self.options
            if self.multi_select:
                multi_select = {
                    'multi_select': True,
                    'show_multi_select_hint': True
                }
            else:
                multi_select = {'multi_select': False}
            
            if self.title:
                menu = TerminalMenu(
                    options,
                    title=self.title,
                    cursor_index=prev_selection,
                    **multi_select
                )
            else:
                menu = TerminalMenu(
                    options,
                    cursor_index=prev_selection,
                    **multi_select
                )

            self.new_cycle()

            selection = menu.show()

            if not self.multi_select:
                if selection is None:
                    self.active = False
                    continue
                
                self.select(options[selection])
                prev_selection = options.index(options[selection])

            else:
                select = [options[option] for option in selection]
                for option in select:
                    self.select(option)


    def enter_once(self):
        '''
        If self.new_cycle has been overwritten, results of the property
        function, then opens the menu in one shot mode
            the selection is passed back to the caller

        Returns:
            the selected option
            OR
            None
        '''
        options = self.options

        if self.multi_select:
            multi_select = {
                'multi_select': True,
                'show_multi_select_hint': True
            }
        else:
            multi_select = {'multi_select': False}

        if self.title:
            menu = TerminalMenu(options, title=self.title, **multi_select)
        else:
            menu = TerminalMenu(options, **multi_select)

        self.new_cycle()

        selection = menu.show()

        if not self.multi_select:
            if selection is None:
                return

            return self.select(options[selection])
        else:
            select = [options[option] for option in selection]
            return self.select(select)


    def new_cycle(self):
        '''
        Overwrite this function to be executed in the enter function before the
        menu appears

        *   The title attribute on the TerminalMenu class behaves poorly
            when given multiline strings, this is a temporary fix to
            circumvent that and present updated contextual data
        '''
        return None


    def select(self, option):
        '''
        Overwrite this function to provide selection handling on the class
        '''
        return option

