"""
A simple progress bar with easily customizable text.
"""


class ProgressBar:
    """
    A simple progress bar with easily customizable text.
    """
    
    def __init__(self, title: str, action: callable, params: list, dictionary: bool) -> None:
        """
        Initialize the progress bar.
        
        :param title: the title that will print above the progress bar.
        :param action: the method to act on the action parameters, must return a string which
        will be displayed next to the progress bar
        :param params: a list of items to act on, must be in the exact format needed for the
        action method. The first item in the list will be looped on.
        :param dictionary: True if the first element of items is a dict
        """
        self.title = title
        self.text = 'initializing'
        self.cur_update = 0
        self.params = params[1:]
        self.items = params[0]
        self.num_updates = len(self.items)
        self.method = action
        self._print_title()
        self._print_bar()
        self._print_text()
        if dictionary:
            for item in self.items:
                self._update(self.items[item])
        else:
            for item in self.items:
                self._update(item)
        self._finalize()
    
    def _update(self, item) -> None:
        self.text = str(self.method(item, *self.params))
        self.cur_update += 1
        self._print_bar()
        self._print_text()
    
    def _print_bar(self) -> None:
        print('\r|', end='')
        i = 0
        cur_pct = (self.cur_update / self.num_updates) * 100
        while i < int(cur_pct):
            if i == 100 / 2 - 3:
                print('{:04.1f}%'.format(cur_pct), end='')
                i += 5
                continue
            if self.cur_update != self.num_updates or i != 99:
                print(u'\u2588', end='')
            i += 1
        while i < 100:
            if i == 100 / 2 - 3:
                print('{:04.1f}%'.format(cur_pct), end='')
                i += 5
                continue
            print(' ', end='')
            i += 1
        print('| ', end='')
    
    def _print_title(self) -> None:
        print(self.title.center(102))
    
    def _print_text(self) -> None:
        print(self.text, end='')
    
    def _finalize(self) -> None:
        print()
