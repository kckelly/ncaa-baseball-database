"""
File to get logos from http://web2.ncaa.org/ncaa_style/img/All_Logos/.

@author: Kevin Kelly
"""
import unicodecsv

from jmu_baseball_utils import data_utils

import os
import requests

from jmu_baseball_utils import file_utils


def get_all_logos() -> None:
    """
    Scrape all logos and save them to 'scraped-data/logos/{school_name}_{size}.gif'. Also creates a
    csv file called 'scraped-data/logos/logo_list.csv' that keeps track of which schools have logos.
    :return: None
    """
    base_url = 'http://web2.ncaa.org/ncaa_style/img/All_Logos/{size}/{school_id}.gif'
    sizes = ['sm', 'lg']  # some schools have both sizes, some only have one or neither
    
    school_id_dict = data_utils.get_school_id_dict()
    
    logo_list = []
    logo_count = 0
    
    for school in school_id_dict:
        for size in sizes:
            url = base_url.format(size=size, school_id=school_id_dict[school])
            
            response = requests.get(url)

            # 200 means it got the page for that url which should include the logo
            if response.status_code == 200:
                print('Logo found: {school} {size}'.format(school=school, size=size))
                logo_file_name = '{logos_path}{school_name}_{size}.gif'.format(
                    logos_path=file_utils.get_logos_directory(), school_name=school, size=size)
    
                # write the logo to file
                with open(logo_file_name, 'wb') as logo_file:
                    logo_file.write(response.content)
                    logo_list.append([school, size, True])
                logo_count += 1

            else:
                print('Logo not found: {school} {size}'.format(school=school, size=size))
                logo_list.append([school, size, False])
    
    # keeps track of whether schools have a logo or not
    logo_csv_name = file_utils.get_logos_csv_name()
    header = ['school_name', 'size', 'logo']
    with open(logo_csv_name, 'wb') as logo_csv:
        writer = unicodecsv.writer(logo_csv)
        writer.writerow(header)
        writer.writerows(logo_list)
    
    print('{} logos found out of {}'.format(logo_count, len(logo_list)))
