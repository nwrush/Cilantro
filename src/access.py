import functools
import inspect
import os.path


class IllegalAccessError(Exception):
    pass


def private(func):
    curframe = inspect.currentframe()
    calframe = inspect.getouterframes(curframe, 2)[1]

    def_file = os.path.splitext(calframe[1])[0]
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)[1]
        
        if os.path.splitext(calframe[1])[0] == def_file:
            return func(*args, **kwargs)
        else:
            raise IllegalAccessError()
    return wrapper
