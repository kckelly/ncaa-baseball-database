import unicodecsv

import DataUtils
import FileUtils

schools = DataUtils.get_school_id_dict()
years = range(2012, 2013)
division = 1
for year in years:
    lines = []
    file_name = FileUtils.get_scrape_file_name(year, division, 'play_by_play')
    with open(file_name, 'rb') as file:
        file_reader = unicodecsv.reader(file)
        next(file_reader)
        for line in file_reader:
            name_changes = {'Incarnate Word': 'UIW', 'LIU Brooklyn': 'LIU',
                            'Coastal Caro.':  'Coastal Carolina', 'Loyola Marymount': 'LMU (CA)'}
            if line[1] in name_changes:
                line[1] = name_changes[line[1]]
            try:
                line[2] = schools[line[1]]
            except:
                print(line[1])
            lines.append(line)
    
    with open(file_name, 'wb') as file:
        file_writer = unicodecsv.writer(file)
        file_writer.writerow(['game_id', 'school_name', 'school_id', 'inning', 'pbp_type',
                              'side', 'pbp_text', 'score_change'])
        file_writer.writerows(lines)
