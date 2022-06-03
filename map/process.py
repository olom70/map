import logging
import os
import prompt_toolkit
import map.tools as tools
import pandas as pd
import matplotlib.pyplot as plt

mlogger = logging.getLogger('map_indicator_app.tools')

@tools.log_function_call
def backup_ok(conninlist: list, backup_full_path_name) -> bool:
    '''
    Backup the in memory database in the specified file
    '''
    try:
        conn_backup = tools.backup_in_memory_db_to_disk(conninlist, backup_full_path_name)[0]
        if conn_backup is not None:
            mlogger.info('The in-memory DB has just been dumped to : {v}'.format(v=backup_full_path_name))
            conn_backup.close()
            return True
        else:
            mlogger.critical(f"The copy of the database in {backup_full_path_name} has failed")
    except BaseException as be:
        mlogger.critical(f'Unexpected error in the function backup() : {be.args}')
        return False

def indicator_connected_at_least_once(conninlist: list, configinlist: list, variables_from_ini_in_dic: list, backup_path: str, current_date: str) -> bool:
    '''
        Generate the indicator "Connect at least once"
        The goal is to follow if each of the declared users in map has connected at least once.
    '''
    for brand in variables_from_ini_in_dic['retailers']:
        branded_query = tools.brand_query(tools.get_queries(configinlist)['connected_at_least_once_v2'], variables_from_ini_in_dic['tables'], brand, variables_from_ini_in_dic['separator'])
        sql_query = pd.read_sql(branded_query, conninlist[0])
        df = pd.DataFrame(sql_query)
        df.plot.barh(stacked=True, x='Teams', title=f'{brand.capitalize()} : status of connections on {current_date}', figsize= (12,7), fontsize=13)
        plt.savefig(backup_path+brand+variables_from_ini_in_dic['separator']+'connected.jpg')


@tools.log_function_call
def processchoice(digit: int, conninlist: list, configinlist: list, variables_from_ini_in_dic: dict) -> bool: 
    try:
        match digit:
            case 0:
                mlogger.info('Choice made : 0, quit the application')
                exit()
            case 1: #generate the indicators
                mlogger.info('Choice made : 1, generate the indicators')
                current_session, current_date = tools.create_current_session(variables_from_ini_in_dic['maindir'],
                                                                                variables_from_ini_in_dic['prefix'],
                                                                                variables_from_ini_in_dic['context'],
                                                                                variables_from_ini_in_dic['separator'])
                backup_full_path_name = current_session + os.path.sep + variables_from_ini_in_dic['backup_name']
                backup_path = current_session + os.path.sep
                if not backup_ok(conninlist, backup_full_path_name):
                    prompt_toolkit.print_formatted_text(prompt_toolkit.HTML('<aaa bg="DarkRed"><Green><b>Copy of the database has failed. Exiting the application. Check the logs</b></Green></aaa>'))
                    exit()
                prompt_toolkit.print_formatted_text(prompt_toolkit.HTML('<aaa bg="LightYellow"><HotPink><b>The Database of current the session is here : %s</b></HotPink></aaa>' %backup_full_path_name ))

                if [indicator_connected_at_least_once(conninlist, configinlist, variables_from_ini_in_dic, backup_path, current_date)]:
                    pass

            case 2: # generate the queries to insert users
                mlogger.info('Choice made : 2, generate the queries to insert users')
            case _:
                pass
        return True
    except BaseException as be:
        mlogger.critical(f'Unexpected error in the function backup() : {be.args}')
        return False
