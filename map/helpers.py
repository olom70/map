from prompt_toolkit import validation
from prompt_toolkit import shortcuts
import prompt_toolkit


def is_ync(text):
    return (text in ('y', 'c'))

validator_yn = validation.Validator.from_callable(
    is_ync,
    error_message="enter (y)es; (n)o, (c)ancel",
    move_cursor_to_end=True)


def is_number(text):
    return text.isdigit()

validator = validation.Validator.from_callable(
    is_number,
    error_message='This input contains non-numeric characters',
    move_cursor_to_end=True)

def process(digit: int): 
    match digit:
        case 0:
            exit()
        case 1:
            prompt_toolkit.print_formatted_text(prompt_toolkit.HTML('<aaa bg="LightYellow"><HotPink><b> %s preparing...</b></HotPink></aaa>' % digit))
        case 2:
            am_I_ok = shortcuts.yes_no_dialog(
                title='Head up !',
                text='Are the input files ready ?"'
            ).run()
            if am_I_ok:
                prompt_toolkit.print_formatted_text(prompt_toolkit.HTML('<aaa bg="LightYellow"><HotPink><b> OK! importing.</b></HotPink></aaa>'))
        case _:
            pass

def are_all_files_ok():
    prompt_toolkit.print_formatted_text(prompt_toolkit.HTML('<aaa bg="LightYellow"><HotPink><b> Welcome to the CGI MAP Janitor ! The indicator provider</b></HotPink></aaa>'))
    prompt_toolkit.print_formatted_text(prompt_toolkit.HTML('<aaa bg="DarkRed"><Green><b> Press y if all the files are ready. :</b></Green></aaa>'))

def welcome():
    prompt_toolkit.print_formatted_text(prompt_toolkit.HTML('<b>---------------------------------</b>'))
    prompt_toolkit.print_formatted_text(prompt_toolkit.HTML('<b>CGI MAP : Generate the indicators</b>'))
    prompt_toolkit.print_formatted_text(prompt_toolkit.HTML('<b>---------------------------------</b>'))
    prompt_toolkit.print_formatted_text(prompt_toolkit.HTML('<aaa bg="LightYellow"><HotPink><b> Choose an Option :</b></HotPink></aaa>'))
    prompt_toolkit.print_formatted_text(prompt_toolkit.HTML('<aaa bg="LightYellow"><HotPink><b> - 0 : Quit</b></HotPink></aaa>'))
    prompt_toolkit.print_formatted_text(prompt_toolkit.HTML('<aaa bg="LightYellow"><HotPink><b> - 1 : Generate the db in the ini file folder</b></HotPink></aaa>'))
    prompt_toolkit.print_formatted_text(prompt_toolkit.HTML('<aaa bg="LightYellow"><HotPink><b> - 2 : Generate the indicators</b></HotPink></aaa>'))