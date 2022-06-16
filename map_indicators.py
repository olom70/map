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
    config = tools.check_ini_files_and_return_config_object(INIFILE)
    if 'Sessions' not in config:
        logger.critical(f'The ini file {INIFILE} is malformed or does not exists. Exiting the application.')
        prompt_toolkit.print_formatted_text(prompt_toolkit.HTML('<aaa bg="DarkRed"><Green><b>The inifile does not exists. Check the logs</b></Green></aaa>'))
        fh.close()
        exit()

    variables_from_ini_in_dic = tools.create_main_variables_from_config(config)
    if variables_from_ini_in_dic is None:
        logger.critical('One of the entry in the ini file triggered a critical error. Exiting the application')
        prompt_toolkit.print_formatted_text(prompt_toolkit.HTML('<aaa bg="DarkRed"><Green><b>One of the entry in the ini file triggered a critical error. Exiting the application. Check the logs</b></Green></aaa>'))
        fh.close()
        exit()
    logger.setLevel(variables_from_ini_in_dic['log_level'])

    helpers.are_all_files_ok()
    input = prompt_toolkit.prompt('Your choice : (y)es/ (c)ancel) : ', validator=helpers.validator_yn)
    if input == 'c':
        prompt_toolkit.print_formatted_text(prompt_toolkit.HTML(f'<aaa bg="LightYellow"><HotPink><b>Goodbye !</b></HotPink></aaa>'))
        logger.info('User canceled the initialisation')
        fh.close()
        exit()

    myconn = tools.initialize_db(':memory:',
                                variables_from_ini_in_dic['retailers'],
                                variables_from_ini_in_dic['retailers_tables'],
                                variables_from_ini_in_dic['toolkit_tables'],
                                variables_from_ini_in_dic['file_ext'],
                                variables_from_ini_in_dic['iniFilesDir'])
    if myconn is None:
        logger.critical('Initialisation of the database failed. Exiting the application')
        prompt_toolkit.print_formatted_text(prompt_toolkit.HTML('<aaa bg="DarkRed"><Green><b>Initialisation of the database failed. Exiting the application. Check the logs</b></Green></aaa>'))
        fh.close()                    
        exit()

    if not tools.queries_are_ok(myconn, config, variables_from_ini_in_dic):
        logger.critical('One the query returned an error while being validated')
        prompt_toolkit.print_formatted_text(prompt_toolkit.HTML('<aaa bg="DarkRed"><Green><b>One the query returned an error while being validated. check The logs</b></Green></aaa>'))
        fh.close()
        exit()

    backup_full_path_name = variables_from_ini_in_dic['iniFilesDir'] + os.path.sep + variables_from_ini_in_dic['backup_name']
    if not process.backup_ok(myconn, backup_full_path_name):
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
            match digit_input:
                case 0:
                    logger.info('Choice made : 0, quit the application')
                    prompt_toolkit.print_formatted_text(prompt_toolkit.HTML('<aaa bg="LightYellow"><HotPink><b>Good Bye !</b></HotPink></aaa>'))
                    fh.close()
                    exit()
                case 1: #backup the DB, then generate the indicators
                    logger.info('Choice made : 1, generate the indicators')
                    
                    # Backup DB
                    
                    prompt_toolkit.print_formatted_text(
                        prompt_toolkit.HTML(
                            '<aaa bg="LightYellow"><HotPink><b>Backing uo the database.</b></HotPink></aaa>')
                    )
                    current_session_path, current_date = tools.create_current_session(
                                                            variables_from_ini_in_dic['maindir'],
                                                            variables_from_ini_in_dic['prefix'],
                                                            variables_from_ini_in_dic['context'],
                                                            variables_from_ini_in_dic['separator']
                                                        )
                    backup_full_path_name = current_session_path + variables_from_ini_in_dic['backup_name']
                    if not process.backup_ok(myconn, backup_full_path_name):
                        prompt_toolkit.print_formatted_text(
                            prompt_toolkit.HTML(
                                '<aaa bg="DarkRed"><Green><b>Copy of the database has failed. Exiting the application. Check the logs</b></Green></aaa>')
                        )
                        fh.close()
                        exit()
                    prompt_toolkit.print_formatted_text(
                        prompt_toolkit.HTML(
                            '<aaa bg="LightYellow"><HotPink><b>The Database of current the session is here : %s</b></HotPink></aaa>' %backup_full_path_name )
                    )

                    # Generate the indicator Connected at least once

                    prompt_toolkit.print_formatted_text(
                        prompt_toolkit.HTML(
                            '<aaa bg="LightYellow"><HotPink><b>Generating the indicator : Connected at least_once.</b></HotPink></aaa>')
                    )
                    if not (process.indicator_connected_at_least_once(
                                        myconn,
                                        config,
                                        variables_from_ini_in_dic,
                                        current_session_path,
                                        current_date)):
                        prompt_toolkit.print_formatted_text(prompt_toolkit.HTML('<aaa bg="DarkRed"><Green><b>Failed to properly compute this indicator  : Connected at least once . Check the logs</b></Green></aaa>'))
                    
                    # Generate the indicator Usage (read/write) break down of the last 4 weeks

                    prompt_toolkit.print_formatted_text(
                        prompt_toolkit.HTML(
                            '<aaa bg="LightYellow"><HotPink><b>Generating the indicator : Usage (read/write).</b></HotPink></aaa>')
                    )

                    if not (process.map_usage(
                                        myconn,
                                        config,
                                        variables_from_ini_in_dic,
                                        current_session_path,
                                        current_date)):
                        prompt_toolkit.print_formatted_text(prompt_toolkit.HTML('<aaa bg="DarkRed"><Green><b>Failed to properly compute this indicator  : Usage by teams . Check the logs</b></Green></aaa>'))

                    prompt_toolkit.print_formatted_text(
                        prompt_toolkit.HTML(
                            '<aaa bg="LightYellow"><HotPink><b>Sending mail.</b></HotPink></aaa>')
                    )
                    
                    if not process.send_yagmail(variables_from_ini_in_dic,
                                                current_session_path,
                                                current_date):
                        prompt_toolkit.print_formatted_text(prompt_toolkit.HTML('<aaa bg="DarkRed"><Green><b>Failure during the email generation. Check the logs</b></Green></aaa>'))

                    prompt_toolkit.print_formatted_text(
                        prompt_toolkit.HTML(
                            '<aaa bg="LightYellow"><HotPink><b>Done. Going back to menu.</b></HotPink></aaa>')
                    )

                case 2: # generate the queries to insert users
                    logger.info('Choice made : 2, generate the queries to insert users')
                case _:
                    pass

if __name__ == '__main__':
    main()
