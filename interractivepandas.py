#%%
from calendar import week
import configparser
import os

from openpyxl import Workbook
from lib.tools import check_ini_files_and_return_config_object, create_main_variables_from_config, initialize_db, get_current_session, get_queries, brand_query
INIFILE = 'map_indicators.ini'
config = configparser.ConfigParser()
config = check_ini_files_and_return_config_object(INIFILE)[0]
variables_from_ini_in_list = create_main_variables_from_config([config])
maindir, separator, retailers, tables, retailers_tables, toolkit_tables, file_ext, iniFilesDir, prefix, context, backup_name, log_level = variables_from_ini_in_list
conn = initialize_db(':memory:', retailers, retailers_tables, toolkit_tables, file_ext, iniFilesDir)[0]
backup_path, current_date = get_current_session(maindir, prefix, context, separator)
backup_path = backup_path+ os.path.sep
all_queries_in_a_dict =  get_queries([config])
#%%
from lib.tools import backup_in_memory_db_to_disk
backup_full_path_name = backup_path + backup_name
conn_backup = backup_in_memory_db_to_disk([conn], backup_full_path_name)[0]

# %%
import pandas as pd
brand = 'pimkie'
branded_query = brand_query(all_queries_in_a_dict['connected_at_least_once_v2'], tables, brand, separator)
sql_query = pd.read_sql(branded_query, conn)
df = pd.DataFrame(sql_query)
print(f'df.index : {df.index}')
print(f'df.columns : {df.columns}')
df
#%%
import matplotlib.pyplot as plt
df.plot.barh(stacked=True, x='Teams', title=f'{brand.capitalize()} : status of connections on {current_date}', figsize= (12,7), fontsize=13)
plt.savefig(backup_path+brand+separator+'connected.jpg')

#%%
import pandas as pd
brand = 'pimkie'
periods = pd.period_range("2022-03-14", "2022-05-22", freq="W")
branded_query = brand_query(all_queries_in_a_dict['request_history'], tables, brand, separator)
#sql_query = pd.read_sql(branded_query, conn, parse_dates='access_date_to_path', index_col='access_date_to_path')
sql_query = pd.read_sql(branded_query, conn)
dfrq = pd.DataFrame(sql_query)
dfrq
#%%
#dfrq.groupby('access_year_week').sum().plot.bar()
#dfrq.assign(entreprise_team=dfrq['entreprise'] + " / " + dfrq['team']).groupby(['entreprise_team']).sum().plot.barh()
#dfrq.groupby([dfrq['entreprise'], dfrq['team'], dfrq['access_year_week']]).sum().plot.barh(stacked=True, title=f'{brand.capitalize()} : activity up to {current_date}', figsize= (15,10), fontsize=13)

dfrq.loc[dfrq['read'] == 'Y'].loc[dfrq['entreprise'] == 'CGI'].loc[dfrq['doNotBotherWith_connectionReminder'] != 'Oui'].groupby([dfrq['access_year_week'], dfrq['entreprise'], dfrq['team']]).sum().plot.barh(stacked=True, title=f'{brand.capitalize()} : VIEW activity up to {current_date} (by Team, Year-WeekNumber)', figsize= (15,10), fontsize=13)
plt.savefig(backup_path+brand+separator+'CGI_view.jpg')
dfrq.loc[dfrq['write'] == 'Y'].loc[dfrq['entreprise'] == 'CGI'].loc[dfrq['doNotBotherWith_connectionReminder'] != 'Oui'].groupby([dfrq['access_year_week'], dfrq['entreprise'], dfrq['team']]).sum().plot.barh(stacked=True, title=f'{brand.capitalize()} : CONTRIBUTE activity up to {current_date} (by Team, Year-WeekNumber)', figsize= (15,10), fontsize=13)
plt.savefig(backup_path+brand+separator+'CGI_contribute.jpg')
dfrq.loc[dfrq['read'] == 'Y'].loc[dfrq['entreprise'] == 'Jules'].loc[dfrq['doNotBotherWith_connectionReminder'] != 'Oui'].groupby([dfrq['access_year_week'], dfrq['entreprise'], dfrq['team']]).sum().plot.barh(stacked=True, title=f'{brand.capitalize()} : VIEW activity up to {current_date} (by Team, Year-WeekNumber)', figsize= (15,10), fontsize=13)
plt.savefig(backup_path+brand+separator+'Jules_view.jpg')
dfrq.loc[dfrq['write'] == 'Y'].loc[dfrq['entreprise'] == 'Jules'].loc[dfrq['doNotBotherWith_connectionReminder'] != 'Oui'].groupby([dfrq['access_year_week'], dfrq['entreprise'], dfrq['team']]).sum().plot.barh(stacked=True, title=f'{brand.capitalize()} : CONTRIBUTE activity up to {current_date} (by Team, Year-WeekNumber)', figsize= (15,10), fontsize=13)
plt.savefig(backup_path+brand+separator+'Jules_contribute.jpg')

#%%
branded_query = brand_query(all_queries_in_a_dict['request_history'], tables, brand, separator)
# dfrq.loc[dfrq['read'] == 'Y'].loc[dfrq['entreprise'] == 'CGI'].loc[dfrq['doNotBotherWith_connectionReminder'] != 'Oui'].groupby([dfrq['access_year_week'], dfrq['entreprise'], dfrq['team']]).sum().plot.barh(stacked=True, title=f'{brand.capitalize()} : VIEW activity up to {current_date} (by Team, Year-WeekNumber)', figsize= (15,10), fontsize=13)
# plt.savefig(backup_path+brand+separator+brand+separator+'CGI_view.jpg')
# dfrq.loc[dfrq['write'] == 'Y'].loc[dfrq['entreprise'] == 'CGI'].loc[dfrq['doNotBotherWith_connectionReminder'] != 'Oui'].groupby([dfrq['access_year_week'], dfrq['entreprise'], dfrq['team']]).sum().plot.barh(stacked=True, title=f'{brand.capitalize()} : CONTRIBUTE activity up to {current_date} (by Team, Year-WeekNumber)', figsize= (15,10), fontsize=13)
# plt.savefig(backup_path+brand+separator+brand+separator+'CGI_contribute.jpg')
dfrq.loc[dfrq['read'] == 'Y'].loc[dfrq['entreprise'] == 'Pimkie'].loc[dfrq['doNotBotherWith_connectionReminder'] != 'Oui'].groupby([dfrq['access_year_week'], dfrq['entreprise'], dfrq['team']]).sum().plot.barh(stacked=True, title=f'{brand.capitalize()} : VIEW activity up to {current_date} (by Team, Year-WeekNumber)', figsize= (15,10), fontsize=13)
plt.savefig(backup_path+brand+separator+brand+separator+'view.jpg')
dfrq.loc[dfrq['write'] == 'Y'].loc[dfrq['entreprise'] == 'Pimkie'].loc[dfrq['doNotBotherWith_connectionReminder'] != 'Oui'].groupby([dfrq['access_year_week'], dfrq['entreprise'], dfrq['team']]).sum().plot.barh(stacked=True, title=f'{brand.capitalize()} : CONTRIBUTE activity up to {current_date} (by Team, Year-WeekNumber)', figsize= (15,10), fontsize=13)
plt.savefig(backup_path+brand+separator+brand+separator+'contribute.jpg')

#%%
dfrq.groupby([dfrq['access_date_to_path'],dfrq['entreprise']]).sum().plot.bar()
#%%
import datetime
datetime.date(2022, 5, 23).isocalendar()[1]
d = '2022-02-15'
print(d[0:4])
print(d[5:7])
print(d[8:])
dfrq
#dfrq_week = dfrq.assign(week_number=datetime.date(dfrq['access_date_to_path'][0:4], dfrq['access_date_to_path'][5:7], dfrq['access_date_to_path'][8:]).isocalendar()[1])
#dfrq_week = dfrq.assign(week_number=(datetime.date(dfrq.access_date_to_path.str[0:4], dfrq.access_date_to_path.str[5:7], dfrq.access_date_to_path.str[8:]).isocalendar()[1]))
dfrq_date_splitted = dfrq.assign(year=dfrq.access_date_to_path.str[0:4], month=dfrq.access_date_to_path.str[5:7], day=dfrq.access_date_to_path.str[8:])
dfrq_week = dfrq_date_splitted.assign(week= datetime.datetime.strptime(dfrq_date_splitted.access_date_to_path, '%Y-%m-%d') .isocalendar()[1])
#dfrq_week.groupby(dfrq_week['week'], dfrq_week['entreprise']).sum.plot.bar()
dfrq_week

# %%
df.to_excel(backup_path+"map.xlsx", index=False, sheet_name='connected_at_teast_once')
sql_query = pd.read_sql(branded_query, conn)
df = pd.DataFrame(sql_query)
df

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
import matplotlib.pyplot as plt
df.plot.barh(stacked=True, x='Teams', title=f'{brand.capitalize()} : status of connections on {current_date}', figsize= (12,7), fontsize=13)
plt.savefig(backup_path+'jules_connected.jpg')

#%%
df.assign(entreprise_team=df["entreprise"] + " " + df["team"]+ " " + df["connected_at_least_once"]).groupby(['entreprise_team']).sum().plot.barh()

#%%
print(df)
df.groupby(['team']).sum()
#%%
for key,val in enumerate(config['Queries']):
    print(f'{key} / {val}')

for val in config['Queries']:
    print(f"{val} : {config['Queries'][val]}")