import os
import json
import re

import xlrd

loc = "~/Documents/Shiksha_Studyabroad_Scraping_data.xlsx"
wb = xlrd.open_workbook(loc)
sheet = wb.sheet_by_index(0)

"""import courses name with respective degree, specialization, and stream id"""
courses_ids = []
course_names = []
for i in range(1, sheet.nrows):
    try:
        course_names.append(sheet.cell_value(i, 1))
        courses_ids.append([sheet.cell_value(i, 1).strip(), int(sheet.cell_value(i, 2)), int(sheet.cell_value(i, 3)), int(sheet.cell_value(i, 4))])
    except ValueError:
        continue

path_to_json = 'jsons_shiksha/'
json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
# print(len(json_files))

for json_file in json_files:
    with open("jsons_shiksha/"+json_file, "r") as json_data:
        data = json.load(json_data)
    # print(data['courses'][0]['course_name'])
    print(data['name_of_the_university'])
    for course in data['courses']:
        # print(course['course_name'])
        # if course['course_name'] in course_names:
        #     # print('course ids exist')
        #     for course_ids in courses_ids:
        #         # print(course_ids)
        #         if course['course_name'] == course_ids[0]:
        #             course['degree'] = course_ids[1]
        #             course['specialization'] = course_ids[2]
        #             course['stream'] = course_ids[3]
        # print(course['tuition_fees'])
        tuition_fee = course['tuition_fees']
        tuition_fee = re.sub('\D', '', tuition_fee)
        course['tuition_fees'] = tuition_fee
        # print(tuition_fee)
    with open("jsons_shiksha/" + json_file, "w") as json_data:
        json.dump(data, json_data, indent=2)
