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

contacts = soup.findAll('div', attrs={"class": "Styled__ContactUsDiv-sc-1yl1nt-10 cNAOeO"})
for contact in contacts:
    print(contact.p.text)


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
        "number_of_programs": None,
        "campus_size": None,
        "no_of_international_students": None,
        "intnl_students_percent": None,
        "on_campus_hostel": None,
        "hostel_fee": None,
        "hostel_fee_currency_id": None,
        "gender_ratio": None,
        "student_faculty_ratio": None,
        "bachelors_masters_ratio": None,
    },
    "institutes_instituteranking": {
        "ranking_authority_id": None,
        "ranking_type_id": None,
        "rank": None,
    },
    "institute_coursefee": {
        "min_fee": None,
        "max_fee": None,
        "currency_id": None,
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

institute = {
    "institute_institute":{

    }
}