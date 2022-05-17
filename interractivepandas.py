#%%
import configparser
import os

from openpyxl import Workbook
from lib.tools import check_ini_files_and_return_config_object, create_main_variables_from_config, initialize_db, get_current_session, get_queries
INIFILE = 'map_indicators.ini'
config = configparser.ConfigParser()
config = check_ini_files_and_return_config_object(INIFILE)[0]
variables_from_ini_in_list = create_main_variables_from_config([config])
maindir, separator, retailers, retailers_tables, toolkit_tables, file_ext, iniFilesDir, prefix, context, backup_name, log_level = variables_from_ini_in_list
conn = initialize_db(':memory:', retailers, retailers_tables, toolkit_tables, file_ext, iniFilesDir)[0]
backup_path = get_current_session(maindir, prefix, context, separator) + os.path.sep
all_queries_in_a_dict =  get_queries([config])





# %%
import pandas as pd


sql_query = pd.read_sql(all_queries_in_a_dict['connected_at_least_once'], conn)
df = pd.DataFrame(sql_query)
print(df)
print(f'df.index : {df.index}')
print(f'df.columns : {df.columns}')

# %%
df.to_excel(backup_path+"map.xlsx", index=False, sheet_name='connected_at_teast_once')

#%%
with pd.ExcelWriter(backup_path+'map.xlsx',
                    mode='a', if_sheet_exists='replace', engine='openpyxl') as writer:
    df.to_excel(writer, index=False, sheet_name='connected_at_teast_once')
#%%
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.worksheet.table import Table, TableStyleInfo
wb = Workbook()
ws = wb.active
index = 0
for index, r in enumerate(dataframe_to_rows(df, index=True, header=True), start=1):
    ws.append(r)
print(index)
ref = 'A1:F'+str(index)
tab = Table(displayName="connected_at_least_once", ref=ref)
style = TableStyleInfo(name="TableStyleDark12", showFirstColumn=False,
                       showLastColumn=False, showRowStripes=True, showColumnStripes=True)
tab.tableStyleInfo = style
ws.add_table(tab)
wb.save(backup_path+'map2.xlsx')
#%%
df.plot.barh()
#%%
df.assign(entreprise_team=df["entreprise"] + " " + df["team"]+ " " + df["connected_at_least_once"]).groupby(['entreprise_team']).sum().plot.barh()

#%%
print(df)
df.groupby(['team']).sum()