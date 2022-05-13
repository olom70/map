import configparser
from sys import exit
import logging
from prompt_toolkit.validation import Validator
from prompt_toolkit.shortcuts import yes_no_dialog
from prompt_toolkit import print_formatted_text, HTML, prompt
# https://htmlcolorcodes.com/fr/noms-de-couleur/
# https://python-prompt-toolkit.readthedocs.io/en/master/pages/getting_started.html
from lib.tools import check_ini_files_and_return_config_object, create_main_variables_from_config, initialize_db
from helpers import are_all_files_ok, validator, validator_yn, welcome, process

logger = logging.getLogger('map_indicator_app')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('map_indicator.log')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)


def main():
    #TODO : pour les indicateurs utiliser la table user_map plutot que adm_user et adm_profile_user
    logger.info('Start. Application is initializing')
    INIFILE = 'map_indicators.ini'
    logger.info(f'The name of the ini file is {INIFILE}')
    config = configparser.ConfigParser()
    config = check_ini_files_and_return_config_object(INIFILE)[0]
    if 'Sessions' not in config:
        logger.critical(f'The ini file {INIFILE} is malformed or does not exists. Exiting the application')
        exit()

    maindir, separator, file_ext, iniFilesDir, prefix, context, backup_name, log_level = str(), str(), str(), str(), str(), str(), str(), str()
    retailers, toolkit_tables = list(), list()
    retailers_tables = dict()
    variables_from_ini_in_list = create_main_variables_from_config([config])
    if variables_from_ini_in_list is None:
        logger.critical('One of the entry in the ini file triggered a critical error. Exiting the application')
        exit()
    maindir, separator, retailers, retailers_tables, toolkit_tables, file_ext, iniFilesDir, prefix, context, backup_name, log_level = variables_from_ini_in_list
    logger.setLevel(log_level)

    are_all_files_ok()
    input = prompt('Your choice : (y)es/ (c)ancel) : ', validator=validator_yn)
    if input == 'c':
        print_formatted_text(HTML(f'<aaa bg="LightYellow"><HotPink><b>Goodbye !</b></HotPink></aaa>'))
        logger.info('User canceled the initialisation')
        fh.close()
        exit()

    conn = initialize_db(':memory:', retailers, retailers_tables, toolkit_tables, file_ext, iniFilesDir)[0]


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
