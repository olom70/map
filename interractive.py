#%%
import configparser
def c() -> list:
    config = configparser.ConfigParser()
    config.read('map_indicators.ini')
    print(config)
    return [config]

config = c()[0]
print(config)


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
def decorate(arg1, arg2, arg3):
    print ('Je suis dans la fonction "decorate".')
    def decorated(func):
        print ('Je suis dans la fonction "decorated".')
        def wrapper(*args, **kwargs):
            print ('Je suis dans la fonction "wrapper".')
            print ("Les arguments du décorateurs sont : %s, %s, %s." % (arg1, arg2, arg3))
            print ("Pré-traitement.")
            print ("Exécution de la fonction %s." % func.__name__)
            response = func(*args, **kwargs)
            print ("Post-traitement.")
            return response
        return wrapper
    return decorated

@decorate("Arg 1", "Arg 2", "Arg 3")
def foobar():
    print ("Je suis foobar, je vous reçois 5 sur 5.")

foobar()
#%%
tables = ['adm_user', 'adm_profile_user']
tool_tables = ['user_acess', 'path']
query = 'select * from adm_user join adm_profile_user on a=a where access = user_access.access_enseigne'
brand = 'jules'
separator = '_'

def brand_query(query: str, tables: list, brand: str, separator: str) -> str:
    branded_tables = [ f'{brand}{separator}{table}' for table in tables ]
    for r in zip(tables, branded_tables):
        query = query.replace(*r)
    branded_query = query.replace('$brand', brand)
    return branded_query

print(query)
query = brand_query(query=query, tables=tables, brand=brand, separator=separator)
print(query)
#%%
s = "The quick brown fox jumps over the lazy dog"
for r in (("brown", "red"), ("lazy", "quick")):
    s = s.replace(*r)
print(s)
#%%
l = []
def f(s: str) -> None:
    if s is not None:
        l.append(s)
        print(id(l))
    if s is None and isinstance(l,list):
        l.clear()

f('5')
print(l)
print(id(l))
f('6')
print(l)
print(isinstance(l, list))
for x in l:
    print(f'l:{x}')
f(None)
print(l)

#%%

retailers_and_cgi = ['a', 'b'] + ['cgi']
print(retailers_and_cgi)
#%%
for i in range(10):
    exec(f"def f_{i}(): print({i})")

for i in range(10):
    exec(f"f_{i}()")

#%%
import pendulum
x = 202230
year = str(x)[0:4]
print(year)
week = str(x)[4:]
print(week)

current_date = '2022-06-24'
extraction_date = pendulum.from_format(current_date, 'YYYY-MM-DD')
x = 202230
year = str(x)[0:4]
print(year)
week = str(x)[4:]

#%%
import datetime as dt
year = 2022
week = 25
last_day_of_the_extracted_week = dt.datetime.strptime(str(year)+ str(week) + '-7', '%G%V-%u').date()
first_day_of_the_extracted_week = dt.datetime.strptime(str(year)+ str(week) + '-1', '%G%V-%u').date()
print(last_day_of_the_extracted_week)
print(first_day_of_the_extracted_week)
#%%
import map.state as state

mystate = state.Mapstate()
mystate.reminder = 'r'
print(mystate.reminder)