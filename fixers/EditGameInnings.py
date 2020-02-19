import copy

import unicodecsv

import DataUtils
import FileUtils

schools = DataUtils.get_school_id_dict()
years = range(2012, 2013)
division = 1
for year in years:
    lines = []
    file_name = FileUtils.get_scrape_file_name(year, division, 'game_innings')
    with open(file_name, 'rb') as file:
        file_reader = unicodecsv.reader(file)
        next(file_reader)
        for line in file_reader:
            name_changes = {'Incarnate Word': 'UIW', 'LIU Brooklyn': 'LIU',
                            'Coastal Caro.':  'Coastal Carolina', 'Loyola Marymount': 'LMU (CA)'}
            if line[3] in name_changes:
                line[3] = name_changes[line[3]]
            try:
                line[4] = schools[line[3]]
            except:
                print(line[3])
            lines.append(line)
    
    with open(file_name, 'wb') as file:
        file_writer = unicodecsv.writer(file)
        file_writer.writerow(['url', 'game_id', 'side', 'school_name', 'school_id'])
        file_writer.writerows(lines)
