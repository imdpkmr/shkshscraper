from bs4 import BeautifulSoup
import requests
import json

url = "https://studyabroad.shiksha.com/usa/universities/harvard-university"
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")
contents = []

title = soup.find('h1', attrs={"class": "H1-sc-1225uyb-0 KmIux"}).text
# print(title)
_, institute_type, established_year = soup.find('div', attrs={"class": "Styled__UnivLinks-sc-132amsi-4 gXZkCE"}).text.split('|')
# print(institute_type)
established_year = ''.join(filter(str.isdigit, established_year))
# print(established_year)

contacts = soup.find_all('div', attrs={"class": "Styled__ContactUsDiv-sc-1yl1nt-10 cNAOeO"})
for contact in contacts:
    pass
    # print(contact.p.text)
data = []
inst_details_table = soup.find('table', attrs={"class": "Styled__TableStyle-sc-10ucg51-0 hfBVJr"})
inst_details_body = inst_details_table.find('tbody')
inst_details_rows = inst_details_body.findAll('tr')
for row in inst_details_rows:
    cols = row.find_all('td')
    cols = [ele.text.strip() for ele in cols]
    data.append([ele for ele in cols if ele])
# for record in data:
#     print(record)

hostel = soup.find('div', attrs={"class": "Styled__OnCampusDiv-sc-1yl1nt-4 ipxyIR"})
# print(hostel.p.text)

app_fee = soup.find('td', string="Application fees")
application_fees = app_fee.find_next_sibling('td').text.split(' ')

rankings = soup.find_all('div', attrs={"class": "Styled__RankingListBox-sc-132amsi-9 iVoSAn"})
# for ranking in rankings:
#     print(ranking.text)
rank = rankings[0].find_all('div')
# for r in rank:
#     print(r.text)
# print(rank[0].text)
# print(rank[2].label.text)
# print(rank[2].p.strong.text)


num_courses = soup.find('div', attrs={"class": "Styled__FindMoreCourseTitle-sc-1yl1nt-57 egsLwJ"}).span.text.split(' ')[0]
# print(num_courses)

intake_month = soup.find_all('div', attrs={"class": "Styled__AdmissionDocumentdiv-sc-1yl1nt-41 dyvnIe"})[5].label.text
# print(intake_month)
num_students = soup.find('div', attrs={"class": "Styled__WikiWidget-sc-1yl1nt-83 jniITB wiki"})
total_students = num_students.findAll('p')[2].strong.text.split(' ')[1]
number_of_students = int(total_students.replace(',',''))
num_of_int_students = int(data[0][1].replace(',', ''))
int_stu_percent = num_of_int_students/number_of_students*100
# print(int_stu_percent)

institute = {
    "institute_institute": {
        "name": title,
        "id": None,
        "short_name": None,
        "established_year": established_year,
        "institute_type": institute_type,
        "country_id": None,
        "state_id": None,
        "city_id": None,
        "brochure": None,
    },
    "institutes_institutecontactdetail": {
        "website": contacts[3].p.text,
        "phone_nos": contacts[1].p.text,
        "fax": None,
        "email_address": contacts[0].p.text,
        "main_address": contacts[2].p.text,
        "latitude": None,
        "longitude": None,
    },
    "institutes_institutedetail": {
        "number_of_programs": ''.join(filter(str.isdigit, num_courses)),
        "campus_size": data[1][1],
        "no_of_international_students": data[0][1],
        "intnl_students_percent": int_stu_percent,
        "on_campus_hostel": hostel.p.text,
        "hostel_fee": data[7][1].split(' ')[1]+" "+data[7][1].split(' ')[2],
        "hostel_fee_currency_id": data[7][1].split(' ')[0],
        "gender_ratio": data[2][1],
        "student_faculty_ratio": data[4][1],
        "bachelors_masters_ratio": data[3][1],
    },
    "institutes_instituteranking": {
        "ranking_authority_id": rank[0].text,
        "ranking_type_id": rank[2].label.text,
        "rank": ''.join(filter(str.isdigit, rank[2].p.strong.text)),
    },
    "institute_coursefee": {
        "min_fee": application_fees[1],
        "max_fee": application_fees[3],
        "currency_id": application_fees[0],
    },
    "institutes_institute_intake": {
        "intake_id": intake_month,
    }
}

json_object = json.dumps(institute, indent=2)

with open("data.json", "w") as outfile:
    outfile.write(json_object)

# print(soup.find('div', attrs={"class": "wiki"}).text)
# print(soup.find('table', attrs={"class": "Styled__TableStyle-sc-10ucg51-0 hfBVJr"}).text)
# tables = soup.findAll('table', attrs={"class": "Styled__TableStyle-sc-10ucg51-0 lfnXDf"})
# index = 1 Established 1636
# for table in tables:
#     if "@media" in table.text:
#         continue
#     print('TABLE DETAILS ' * index)
#     rows = table.findAll('tr')
#     for row in rows:
        # print(row.text)
# table_data = [[cell.text for cell in row("td")] for row in BeautifulSoup(response.content, "html.parser")("tr")]
# print(table_data)
# for data in table_data:
    # print(data)
