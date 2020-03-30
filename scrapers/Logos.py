"""
File to get logos from http://web2.ncaa.org/ncaa_style/img/All_Logos/.

@author: Kevin Kelly
"""
import unicodecsv

import DataUtils

import os
import requests



def get_all_logos():
    """
    Scrape all logos and save them to 'scraped-data/logos/{school_name}_{size}.gif'. Also creates a
    csv file called 'scraped-data/logos/logo_list.csv' that keeps track of which schools have logos.
    :return: None
    """
    base_url = 'http://web2.ncaa.org/ncaa_style/img/All_Logos/{size}/{school_id}.gif'
    sizes = ['sm', 'lg']  # some schools have both sizes, some only have one or neither
    
    if not os.path.exists('../scraped-data/logos/'):
        os.makedirs('../scraped-data/logos/')
    
    school_id_dict = DataUtils.get_school_id_dict()
    
    logo_list = []
    logo_count = 0
    
    for school in school_id_dict:
        for size in sizes:
            url = base_url.format(size=size, school_id=school_id_dict[school])
            
            response = requests.get(url)

            # 200 means it got the page for that url which should include the logo
            if response.status_code == 200:
                print('Logo found: {school} {size}'.format(school=school, size=size))
                logo_file_name = '../scraped-data/logos/{school_name}_{size}.gif'.format(
                    school_name=school, size=size)
    
                # write the logo to file
                with open(logo_file_name, 'wb') as logo_file:
                    logo_file.write(response.content)
                    logo_list.append([school, size, True])
                logo_count += 1

            else:
                print('Logo not found: {school} {size}'.format(school=school, size=size))
                logo_list.append([school, size, False])

    # keeps track of whether schools have a logo or not
    logo_csv_name = '../scraped-data/logos/logo_list.csv'
    header = ['school_name', 'size', 'logo']
    with open(logo_csv_name, 'wb') as logo_csv:
        writer = unicodecsv.writer(logo_csv)
        writer.writerow(header)
        writer.writerows(logo_list)
    
    print('{} logos found out of {}'.format(logo_count, len(logo_list)))
