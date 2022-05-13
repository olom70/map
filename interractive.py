#%%
import configparser
config = configparser.ConfigParser()
config.read('map_indicators.ini')
config.sections()
tables = config['Database']['tables'].split()
print(tables)

# %%
import configparser

def init(inifile : str) -> bool:
    '''
        check if everything is ok prior to entering the main loop
    '''
    config = configparser.ConfigParser()
    config.read(inifile)
    if 'Database' in config and 'Sessions' in config:
        return True
    else:
        return False

assert init('map_indicators.ini') is True
assert init('m') is False




# %%
import os
import platform
print(os.name)
print(platform.system())
# %%

def decorate(func):
    def wrapper(arg1):
        a = list(arg1)
        prefix = 'jules'
        separator = '_'
        newlist = [ f'{prefix}{separator}{table}' for table in a]
        func(newlist)
    return wrapper


@decorate
def select(tablelist: list) -> None:
    for value in tablelist:
        print(f'select * from{value}')

l = ['t1', 't2']
select(l)





# %%
def decorate(func):
    print(u"Je suis dans la fonction 'decorate' et je décore '%s.'" % func.__name__)
    def wrapper(*args, **kwargs):
        print(u"Je suis dans la fonction 'wrapper' qui accède aux arguments de '%s'." % func.__name__)
        a = list(args)
        a.reverse()
        print(u"J'en donne la preuve, je peux les inverser : %s." % ', '.join(a))
        print(u"Exécution de la fonction '%s'." % func.__name__)
        response = func(*args)
        print(u"Je peux effectuer, ici, un post-traitement.")
        return response
    return wrapper

# Notre fonction décorée
@decorate
def foobar(*args):
    print(", ".join(args))

# Appel de la fonction
foobar("A", "B", "C", "D")
# %%
# It’s not black magic, you just have to let the wrapper 
# pass the argument:

def a_decorator_passing_arguments(function_to_decorate):
    def a_wrapper_accepting_arguments(arg1, arg2):
        print("I got args! Look: {0}, {1}".format(arg1, arg2))
        function_to_decorate(arg1, arg2)
    return a_wrapper_accepting_arguments

# Since when you are calling the function returned by the decorator, you are
# calling the wrapper, passing arguments to the wrapper will let it pass them to 
# the decorated function

@a_decorator_passing_arguments
def print_full_name(first_name, last_name):
    print("My name is {0} {1}".format(first_name, last_name))
    
print_full_name("Peter", "Venkman")
# outputs:
#I got args! Look: Peter Venkman
#My name is Peter Venkman
# %%
def add_prefix(arg1):
    def decorate(func):
        def wrapper(*args):
            prefix = arg1
            a = list(args[0])
            separator = '_'
            newlist = [ f'{prefix}{separator}{table}' for table in a]
            func(newlist)
        return wrapper
    return decorate


@add_prefix('jules')
def select(tablelist: list) -> None:
    for value in tablelist:
        print(f'select * from{value}')

l = ['t1', 't2']
select(l)

# %%
myvar = 'content'
print('content of variable {v.__name__} {v}'.format(v=myvar))
# %%
import datetime
print(datetime.datetime.today())
# %%
context = 'datetime'
current_context = datetime.date.today() if context == 'date' else datetime.datetime.today()
print(current_context)
# %%
var = '/path/to/Session-2022-05-14-14'
session = var[var.rfind('-')+1:]
print(session)
# %%
returned_paths = ['/path/to/Session-2022-05-14-14', '/path/to/Session-2022-05-14-2']
current_context = str(datetime.date.today() if context == 'date' else datetime.datetime.today())
separator = '-'
sessions = [1]
for path in returned_paths:
    sessions.append(int(path[path.rfind('-')+1:]))
x = max(sessions)
path_to_create = current_context+separator+str((max(sessions)+1))
print(path_to_create)
print(sessions)
print(x)

# %%
from prompt_toolkit import print_formatted_text, HTML, prompt
from prompt_toolkit.validation import Validator
def is_ync(text):
    return True if (text=='y' or text =='n' or text == 'c') else False

validator_yn = Validator.from_callable(
    is_ync,
    error_message='enter (y)es; (n)o, (c)ancel',
    move_cursor_to_end=True)

inputt = prompt('Your choice : (y/n/c) : ')
# %%
def ask_ok(prompt, retries=4, reminder='Please try again!'):
    while True:
        ok = input(prompt)
        if ok in ('y', 'ye', 'yes'):
            return True
        if ok in ('n', 'no', 'nop', 'nope'):
            return False
        retries = retries - 1
        if retries < 0:
            raise ValueError('invalid user response')
        print(reminder)

ask_ok('?')
# %%
