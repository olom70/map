import logging
import os
import map.tools as tools
mlogger = logging.getLogger('map_indicator_app.tools')


def backup(conninlist: list, variables_from_ini_in_list: list, where = ('ini', 'session')) -> str:
    '''
    Backup the in memory database in the specified file
    '''
    try:
        conn = conninlist[0]
        maindir, separator, retailers, tables, retailers_tables, toolkit_tables, file_ext, iniFilesDir, prefix, context, backup_name, log_level = variables_from_ini_in_list

        match(where):
            case 'session':
                current_session, current_date = tools.get_current_session(maindir, prefix, context, separator)
                backup_full_path_name = current_session + os.path.sep + backup_name
                backup_path = current_session + os.path.sep
            case('ini'):
                backup_full_path_name = maindir + os.path.sep + iniFilesDir + os.path.sep + backup_name
        conn_backup = tools.backup_in_memory_db_to_disk([conn], backup_full_path_name)[0]
        if conn_backup is not None:
            mlogger.info('The in-memory DB has just been dumped to : {v}'.format(v=backup_full_path_name))
            conn_backup.close()
            return backup_full_path_name
    except BaseException as be:
        mlogger.critical(f'Unexpected error in the function backup() : {be.args}')
        return None