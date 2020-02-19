import copy

import unicodecsv

import DataUtils
import FileUtils

schools = DataUtils.get_school_id_dict()
years = range(2012, 2013)
division = 1
for year in years:
    lines = []
    file_name = FileUtils.get_scrape_file_name(year, division, 'game_info')
    with open(file_name, 'rb') as file:
        file_reader = unicodecsv.DictReader(file)
        header = copy.copy(file_reader.fieldnames)
        header.insert(4, 'away_team_sport_id')
        header.insert(7, 'home_team_sport_id')
        for line in file_reader:
            name_changes = {'Incarnate Word': 'UIW', 'LIU Brooklyn': 'LIU',
                            'Coastal Caro.': 'Coastal Carolina', 'Loyola Marymount': 'LMU (CA)'}
            if line['away_school_name'] in name_changes:
                line['away_school_name'] = name_changes[line['away_school_name']]
            elif line['home_school_name'] in name_changes:
                line['home_school_name'] = name_changes[line['home_school_name']]
            line.update({'away_team_sport_id': line['away_school_id'],
                         'home_team_sport_id': line['home_school_id']})
            try:
                line['away_school_id'] = schools[line['away_school_name']]
            except:
                print(line['away_school_name'])
            try:
                line['home_school_id'] = schools[line['home_school_name']]
            except:
                print(line['home_school_name'])
            lines.append(line)
    
    with open(file_name, 'wb') as file:
        file_writer = unicodecsv.DictWriter(file, header)
        file_writer.writeheader()
        file_writer.writerows(lines)
