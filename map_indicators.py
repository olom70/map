import configparser
from sys import exit
from prompt_toolkit.validation import Validator
from prompt_toolkit.shortcuts import yes_no_dialog
from prompt_toolkit import print_formatted_text, HTML, prompt
# https://htmlcolorcodes.com/fr/noms-de-couleur/
# https://python-prompt-toolkit.readthedocs.io/en/master/pages/getting_started.html
from lib.tools import check_ini_files_and_return_config_object, create_main_variables_from_config

def is_number(text):
    return text.isdigit()

validator = Validator.from_callable(
    is_number,
    error_message='This input contains non-numeric characters',
    move_cursor_to_end=True)

def process(digit: int): 
    match digit:
        case 0:
            exit()
        case 1:
            print_formatted_text(HTML('<aaa bg="LightYellow"><HotPink><b> %s preparing...</b></HotPink></aaa>' % digit))
        case 2:
            am_I_ok = yes_no_dialog(
                title='Head up !',
                text='Are the input files ready ?"'
            ).run()
            if am_I_ok:
                print_formatted_text(HTML('<aaa bg="LightYellow"><HotPink><b> OK! importing.</b></HotPink></aaa>'))

def welcome():
    print_formatted_text(HTML('<b>---------------------------------</b>'))
    print_formatted_text(HTML('<b>CGI MAP : Generate the indicators</b>'))
    print_formatted_text(HTML('<b>---------------------------------</b>'))
    print_formatted_text(HTML('<aaa bg="LightYellow"><HotPink><b> Choose an Option :</b></HotPink></aaa>'))
    print_formatted_text(HTML('<aaa bg="LightYellow"><HotPink><b> - 0 : Quit</b></HotPink></aaa>'))
    print_formatted_text(HTML('<aaa bg="LightYellow"><HotPink><b> - 1 : prepare the files</b></HotPink></aaa>'))
    print_formatted_text(HTML('<aaa bg="LightYellow"><HotPink><b> - 2 : import the content</b></HotPink></aaa>'))
    print_formatted_text(HTML('<aaa bg="LightYellow"><HotPink><b> - 3 : Remove the backup tables (a prompt will ask to confirm)</b></HotPink></aaa>'))

def main():
    INIFILE = 'map_indicator.py'
    config = configparser.ConfigParser()
    config = check_ini_files_and_return_config_object(inifile=INIFILE)[0]
    if 'Session' not in config:
        exit()
    maindir, separator, file_ext, iniFilesDir, prefix, context, backup_name = str(), str(), str(), str(), str(), str(), str()
    retailers, toolkit_tables = list(), list()
    retailers_tables = dict()
    
    maindir, separator, retailers, retailers_tables, toolkit_tables, 
    file_ext, iniFilesDir, prefix, context,
    backup_name = create_main_variables_from_config([config])
    
    if maindir is None:
        exit()


    while True:
        welcome()
        try:
            digit_input = int(prompt('Give a number: ', validator=validator))
        except KeyboardInterrupt:
            continue
        except EOFError:
            break
        else:
            process(digit_input)
    print('GoodBye!')

if __name__ == '__main__':
    main()
