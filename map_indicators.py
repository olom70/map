import configparser
from sys import exit
import logging
import os
import prompt_toolkit
import map.process as process
# https://htmlcolorcodes.com/fr/noms-de-couleur/
# https://python-prompt-toolkit.readthedocs.io/en/master/pages/getting_started.html
from map import tools
from map import helpers

logger = logging.getLogger('map_indicator_app')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('map_indicator.log')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)


def main():
    logger.info('Start. Application is initializing')
    INIFILE = 'map_indicators.ini'
    logger.info(f'The name of the ini file is {INIFILE}')
    config = configparser.ConfigParser()
    config = tools.check_ini_files_and_return_config_object(INIFILE)[0]
    if 'Sessions' not in config:
        logger.critical(f'The ini file {INIFILE} is malformed or does not exists. Exiting the application.')
        prompt_toolkit.print_formatted_text(prompt_toolkit.HTML('<aaa bg="DarkRed"><Green><b>The inifile does not exists. Check the logs</b></Green></aaa>'))
        exit()

    variables_from_ini_in_dic = tools.create_main_variables_from_config([config])
    if variables_from_ini_in_dic is None:
        logger.critical('One of the entry in the ini file triggered a critical error. Exiting the application')
        prompt_toolkit.print_formatted_text(prompt_toolkit.HTML('<aaa bg="DarkRed"><Green><b>One of the entry in the ini file triggered a critical error. Exiting the application. Check the logs</b></Green></aaa>'))
        exit()
    logger.setLevel(variables_from_ini_in_dic['log_level'])

    if not tools.queries_are_ok(conninlist, [config], variables_from_ini_in_dic):
        logger.critical('One the query returned an error while being validated')
        prompt_toolkit.print_formatted_text(prompt_toolkit.HTML('<aaa bg="DarkRed"><Green><b>One the query returned an error while being validated. check The logs</b></Green></aaa>'))
        exit()

    helpers.are_all_files_ok()
    input = prompt_toolkit.prompt('Your choice : (y)es/ (c)ancel) : ', validator=helpers.validator_yn)
    if input == 'c':
        prompt_toolkit.print_formatted_text(prompt_toolkit.HTML(f'<aaa bg="LightYellow"><HotPink><b>Goodbye !</b></HotPink></aaa>'))
        logger.info('User canceled the initialisation')
        fh.close()
        exit()

    conninlist = tools.initialize_db(':memory:',
                                variables_from_ini_in_dic['retailers'],
                                variables_from_ini_in_dic['retailers_tables'],
                                variables_from_ini_in_dic['toolkit_tables'],
                                variables_from_ini_in_dic['file_ext'],
                                variables_from_ini_in_dic['iniFilesDir'])
    if conninlist[0] is None:
        logger.critical('Initialisation of the database failed. Exiting the application')
        prompt_toolkit.print_formatted_text(prompt_toolkit.HTML('<aaa bg="DarkRed"><Green><b>Initialisation of the database failed. Exiting the application. Check the logs</b></Green></aaa>'))
        exit()

    backup_full_path_name = variables_from_ini_in_dic['iniFilesDir'] + os.path.sep + variables_from_ini_in_dic['backup_name']
    if not process.backup_ok(conninlist, backup_full_path_name):
        prompt_toolkit.print_formatted_text(prompt_toolkit.HTML('<aaa bg="DarkRed"><Green><b>Copy of the database has failed. Exiting the application. Check the logs</b></Green></aaa>'))
 
    while True:
        helpers.welcome()
        try:
            digit_input = int(prompt_toolkit.prompt('Give a number: ', validator=helpers.validator))
        except KeyboardInterrupt:
            continue
        except EOFError:
            break
        else:
            if not (helpers.processchoice(digit_input, conninlist, [config], variables_from_ini_in_dic)):
                prompt_toolkit.print_formatted_text(prompt_toolkit.HTML('<aaa bg="DarkRed"><Green><b>Something unexpected happened while processing the choice. Check the logs</b></Green></aaa>'))
                exit()
    print('GoodBye!')
    fh.close()

if __name__ == '__main__':
    main()
