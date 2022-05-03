from sys import exit
from prompt_toolkit.validation import Validator
from prompt_toolkit.shortcuts import yes_no_dialog
from prompt_toolkit import print_formatted_text, HTML, prompt
# https://htmlcolorcodes.com/fr/noms-de-couleur/


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
