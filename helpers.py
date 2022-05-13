from prompt_toolkit.validation import Validator
from prompt_toolkit.shortcuts import yes_no_dialog
from prompt_toolkit import print_formatted_text, HTML


def is_ync(text):
    return (text in ('y', 'c'))

validator_yn = Validator.from_callable(
    is_ync,
    error_message="enter (y)es; (n)o, (c)ancel",
    move_cursor_to_end=True)


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

def are_all_files_ok():
    print_formatted_text(HTML('<aaa bg="LightYellow"><HotPink><b> Welcome to the CGI MAP Janitor ! The indicator provider</b></HotPink></aaa>'))
    print_formatted_text(HTML('<aaa bg="DarkRed"><Green><b> Press y if all the files are ready. :</b></Green></aaa>'))

def welcome():
    print_formatted_text(HTML('<b>---------------------------------</b>'))
    print_formatted_text(HTML('<b>CGI MAP : Generate the indicators</b>'))
    print_formatted_text(HTML('<b>---------------------------------</b>'))
    print_formatted_text(HTML('<aaa bg="LightYellow"><HotPink><b> Choose an Option :</b></HotPink></aaa>'))
    print_formatted_text(HTML('<aaa bg="LightYellow"><HotPink><b> - 0 : Quit</b></HotPink></aaa>'))
    print_formatted_text(HTML('<aaa bg="LightYellow"><HotPink><b> - 1 : Generate Indicators In Excel</b></HotPink></aaa>'))
    print_formatted_text(HTML('<aaa bg="LightYellow"><HotPink><b> - 2 : Plot indicators</b></HotPink></aaa>'))
    print_formatted_text(HTML('<aaa bg="LightYellow"><HotPink><b> - 3 : Remove the backup tables (a prompt will ask to confirm)</b></HotPink></aaa>'))
