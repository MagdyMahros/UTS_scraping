"""Description:
    * author: Magdy Abdelkader
    * company: Fresh Futures/Seeka Technology
    * position: IT Intern
    * date: 03-11-20
    * description:This script extracts the corresponding undergraduate courses details and tabulate it.
"""

import csv
import re
import time
from pathlib import Path
from selenium import webdriver
import bs4 as bs4
import os
import copy
from CustomMethods import TemplateData
from CustomMethods import DurationConverter as dura

option = webdriver.ChromeOptions()
option.add_argument(" - incognito")
option.add_argument("headless")
exec_path = Path(os.getcwd().replace('\\', '/'))
exec_path = exec_path.parent.__str__() + '/Libraries/Google/v86/chromedriver.exe'
browser = webdriver.Chrome(executable_path=exec_path, options=option)

# read the url from each file into a list
course_links_file_path = Path(os.getcwd().replace('\\', '/'))
course_links_file_path = course_links_file_path.__str__() + '/UTS_postgrad_links.txt'
course_links_file = open(course_links_file_path, 'r')

# the csv file we'll be saving the courses to
csv_file_path = Path(os.getcwd().replace('\\', '/'))
csv_file = csv_file_path.__str__() + '/UTS_postgrad.csv'

course_data = {'Level_Code': '', 'University': 'University of Technology Sydney', 'City': '', 'Country': 'Australia',
               'Course': '', 'Int_Fees': '', 'Local_Fees': '', 'Currency': 'AUD', 'Currency_Time': 'year',
               'Duration': '', 'Duration_Time': '', 'Full_Time': '', 'Part_Time': '', 'Prerequisite_1': '',
               'Prerequisite_2': 'IELTS', 'Prerequisite_3': '', 'Prerequisite_1_grade': '',
               'Prerequisite_2_grade': '6.5',
               'Prerequisite_3_grade': '', 'Website': '', 'Course_Lang': '', 'Availability': '', 'Description': '',
               'Career_Outcomes': '', 'Online': '', 'Offline': '', 'Distance': '', 'Face_to_Face': '',
               'Blended': '', 'Remarks': ''}

possible_cities = {'rockhampton': 'Rockhampton', 'cairns': 'Cairns', 'bundaberg': 'Bundaberg',
                   'townsville': 'Townsville', 'canberra': 'Canberra', 'paddington': 'Paddington',
                   'online': 'Online', 'gladstone': 'Gladstone', 'mackay': 'Mackay', 'mixed': 'Online',
                   'yeppoon': 'Yeppoon', 'brisbane': 'Brisbane', 'sydney': 'Sydney', 'queensland': 'Queensland',
                   'melbourne': 'Melbourne', 'albany': 'Albany', 'perth': 'Perth', 'adelaide': 'Adelaide',
                   'noosa': 'Noosa', 'emerald': 'Emerald', 'hawthorn': 'Hawthorn', 'wantirna': 'Wantirna',
                   'prahran': 'Prahran', 'kensington': 'Kensington', 'moore park': 'New South Wales'}

possible_languages = {'Japanese': 'Japanese', 'French': 'French', 'Italian': 'Italian', 'Korean': 'Korean',
                      'Indonesian': 'Indonesian', 'Chinese': 'Chinese', 'Spanish': 'Spanish'}

course_data_all = []
level_key = TemplateData.level_key  # dictionary of course levels
faculty_key = TemplateData.faculty_key  # dictionary of course levels

# GET EACH COURSE LINK
for each_url in course_links_file:
    actual_cities = []
    remarks_list = []
    browser.get(each_url)
    pure_url = each_url.strip()
    each_url = browser.page_source

    soup = bs4.BeautifulSoup(each_url, 'lxml')
    time.sleep(1)

    # SAVE COURSE URL
    course_data['Website'] = pure_url

    # SAVE COURSE TITLE
    title_div = soup.find('div', class_='page-title')
    if title_div:
        title = title_div.find('h1')
        if title:
            course_data['Course'] = title.get_text()
        print('COURSE TITLE: ', course_data['Course'])

    # DECIDE THE LEVEL CODE
    for i in level_key:
        for j in level_key[i]:
            if j in course_data['Course']:
                course_data['Level_Code'] = i
    print('COURSE LEVEL CODE: ', course_data['Level_Code'])

    # DECIDE THE FACULTY
    for i in faculty_key:
        for j in faculty_key[i]:
            if j.lower() in course_data['Course'].lower():
                course_data['Faculty'] = i
    print('COURSE FACULTY: ', course_data['Faculty'])

    # COURSE DESCRIPTION
    desc_tag = soup.find('div', class_='js-read-more read-more')
    if desc_tag:
        desc_p = desc_tag.find('p')
        if desc_p:
            course_data['Description'] = desc_p.get_text()

    # COURSE LANGUAGE
    for language in possible_languages:
        if language in course_data['Course']:
            course_data['Course_Lang'] = language
        else:
            course_data['Course_Lang'] = 'English'
    print('COURSE LANGUAGE: ', course_data['Course_Lang'])

    # DURATION & DURATION_TIME / PART-TIME & FULL-TIME
    duration_tag = soup.find('h4', class_='collapsible__title', text=re.compile('Course duration', re.IGNORECASE))
    if duration_tag:
        duration_list = []
        dura_div = duration_tag.find_next('div', class_='collapsible__content')
        if dura_div:
            dura_ps = dura_div.find_all('p')
            if dura_ps:
                for element in dura_ps:
                    duration_list.append(element.get_text().lower())
                duration_list = ' '.join(duration_list)
                print(duration_list)
                if 'on campus' in duration_list:
                    course_data['Face_to_Face'] = 'yes'
                    course_data['Offline'] = 'yes'
                else:
                    course_data['Face_to_Face'] = 'no'
                    course_data['Offline'] = 'no'
                if 'full-time' in duration_list:
                    course_data['Full_Time'] = 'yes'
                else:
                    course_data['Full_Time'] = 'no'
                if 'part-time' in duration_list:
                    course_data['Part_Time'] = 'yes'
                else:
                    course_data['Part_Time'] = 'no'
                convertedDuration = dura.convert_duration(duration_list)
                if convertedDuration:
                    duration_l = list(convertedDuration)
                    if duration_l[0] == 1 and 'Years' in duration_l[1]:
                        duration_l[1] = 'Year'
                    if duration_l[0] == 1 and 'Months' in duration_l[1]:
                        duration_l[1] = 'Month'
                    course_data['Duration'] = duration_l[0]
                    course_data['Duration_Time'] = duration_l[1]
                    print('COURSE DURATION: ', str(duration_l[0]) + ' / ' + duration_l[1])
                print('FULL-TIME/PART-TIME: ', course_data['Full_Time'] + ' / ' + course_data['Part_Time'])
    #CITY
    location_title = soup.find('h3', class_='sidebar__info-title', text=re.compile('Location', re.IGNORECASE))
    if location_title:
        city = location_title.find_next('p')
        city_text = city.get_text().lower()
        if 'city campus' in city_text:
            actual_cities.append('sydney')
        if 'distance' in city_text:
            actual_cities.append('online')
            course_data['Distance'] = 'yes'
        else:
            course_data['Distance'] = 'no'
        if 'online' in city_text:
            actual_cities.append('online')
            course_data['Online'] = 'yes'
        else:
            course_data['Online'] = 'no'
        print('CITY: ', actual_cities)

    # duplicating entries with multiple cities for each city
    for i in actual_cities:
        course_data['City'] = possible_cities[i]
        course_data_all.append(copy.deepcopy(course_data))
    del actual_cities


    # TABULATE THE DATA
    desired_order_list = ['Level_Code', 'University', 'City', 'Course', 'Faculty', 'Int_Fees', 'Local_Fees',
                          'Currency', 'Currency_Time', 'Duration', 'Duration_Time', 'Full_Time', 'Part_Time',
                          'Prerequisite_1', 'Prerequisite_2', 'Prerequisite_3', 'Prerequisite_1_grade',
                          'Prerequisite_2_grade', 'Prerequisite_3_grade', 'Website', 'Course_Lang', 'Availability',
                          'Description', 'Career_Outcomes', 'Country', 'Online', 'Offline', 'Distance',
                          'Face_to_Face',
                          'Blended', 'Remarks']

    course_dict_keys = set().union(*(d.keys() for d in course_data_all))

    with open(csv_file, 'w', encoding='utf-8', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, course_dict_keys)
        dict_writer.writeheader()
        dict_writer.writerows(course_data_all)

    with open(csv_file, 'r', encoding='utf-8') as infile, open('UTS_postgrad_ordered.csv', 'w', encoding='utf-8',
                                                               newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=desired_order_list)
        # reorder the header first
        writer.writeheader()
        for row in csv.DictReader(infile):
            # writes the reordered rows to the new file
            writer.writerow(row)


