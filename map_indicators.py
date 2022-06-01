import configparser
from sys import exit
import logging
import prompt_toolkit
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
        logger.critical(f'The ini file {INIFILE} is malformed or does not exists. Exiting the application. Check the logs')
        exit()

    maindir, separator, file_ext, iniFilesDir, prefix, context, backup_name, log_level = str(), str(), str(), str(), str(), str(), str(), str()
    tables, retailers, toolkit_tables = list(), list(), list()
    retailers_tables = dict()
    variables_from_ini_in_list = tools.create_main_variables_from_config([config])
    if variables_from_ini_in_list is None:
        logger.critical('One of the entry in the ini file triggered a critical error. Exiting the application. Check the logs')
        exit()
    maindir, separator, retailers, tables, retailers_tables, toolkit_tables, file_ext, iniFilesDir, prefix, context, backup_name, log_level = variables_from_ini_in_list
    logger.setLevel(log_level)

    helpers.are_all_files_ok()
    input = prompt_toolkit.prompt('Your choice : (y)es/ (c)ancel) : ', validator=helpers.validator_yn)
    if input == 'c':
        prompt_toolkit.print_formatted_text(prompt_toolkit.HTML(f'<aaa bg="LightYellow"><HotPink><b>Goodbye !</b></HotPink></aaa>'))
        logger.info('User canceled the initialisation')
        fh.close()
        exit()

    conn = tools.initialize_db(':memory:', retailers, retailers_tables, toolkit_tables, file_ext, iniFilesDir)[0]
    if conn is None:
        logger.critical('Initialisation of the databse failed. Exiting the application. Check the logs')


    while True:
        helpers.welcome()
        try:
            digit_input = int(prompt_toolkit.prompt('Give a number: ', validator=helpers.validator))
        except KeyboardInterrupt:
            continue
        except EOFError:
            break
        else:
            helpers.process(digit_input)
    print('GoodBye!')
    fh.close()

if __name__ == '__main__':
    main()
