"""
Removes all tables from the database to clear them and adds them back in with the new set up. To add all the tables,
this program simply combines all files in table-definitions and function-definitions from the database_files
directory into one file (called add_tables.sql) then runs a psql command that executes the sql code in the file.
Note: You must be careful about the order of the files in this program, if there is a foreign key from a table that
is not created yet this program will fail.
"""

from database_files.ncaa_database import NCAADatabase

text = input('Are you sure you want to reset the tables in the database? WARNING: This will remove all data in the '
             'database.(y/n)')
if text.lower() != 'y':
    print('Input other than y received, cancelling reset of database and exiting.')
    exit(0)

with NCAADatabase() as database:
    type_directory = 'database_files/type-definitions/'
    type_list = ['class', 'side', 'pos', 'ump_pos']
    
    table_directory = 'database_files/table-definitions/'
    table_list = ['year_info', 'conference', 'school', 'coach', 'stadium', 'team', 'player', 'roster',
                  'game', 'inning', 'play_by_play', 'game_position', 'hitting_line',
                  'pitching_line', 'fielding_line', 'umpire', 'game_umpire']
    function_directory = 'database_files/function-definitions/'
    function_list = ['player_year_totals_fielding', 'player_year_totals_hitting', 'player_year_totals_pitching',
                     'team_year_totals_fielding', 'team_year_totals_hitting', 'team_year_totals_pitching']
    
    for table in table_list[::-1]:
        database.cursor.execute(f'DROP TABLE IF EXISTS {table}')
    
    for custom_type in type_list:
        database.cursor.execute(f'DROP TYPE IF EXISTS {custom_type}')
    
    type_files = [f'{type_directory}/{custom_type}.sql' for custom_type in type_list]
    
    table_files = [f'{table_directory}/{table}.sql' for table in table_list]
    
    function_files = [f'{function_directory}/{function}.sql' for function in function_list]
    
    all_files = type_files + table_files + function_files
    
    for file in all_files:
        database.cursor.execute(open(file, 'r').read())
    database.cursor.copy_expert("COPY year_info FROM STDIN WITH delimiter ',' NULL AS '' CSV HEADER",
                                open('database_files/csv-data/year_info.csv', 'r'))
