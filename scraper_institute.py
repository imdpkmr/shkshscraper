from bs4 import BeautifulSoup
import requests
import json


def write_json(institute, university_name=""):
    json_object = json.dumps(institute, indent=2)
    filename = "json/"+university_name+"_data.json"
    with open(filename, "w") as outfile:
        outfile.write(json_object)

def scrape_institute(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    contents = []

    title = soup.find('h1', attrs={"class": "H1-sc-1225uyb-0 KmIux"}).text
    # print(title)
    _, institute_type, established_year = soup.find('div', attrs={
        "class": "Styled__UnivLinks-sc-132amsi-4 gXZkCE"}).text.split('|')
    # print(institute_type)
    established_year = ''.join(filter(str.isdigit, established_year))
    # print(established_year)

    contacts = soup.find_all('div', attrs={"class": "Styled__ContactUsDiv-sc-1yl1nt-10 cNAOeO"})
    for contact in contacts:
        pass
        # print(contact.p.text)
    data = []
    institute_details = {}
    inst_details_table = soup.find('table', attrs={"class": "Styled__TableStyle-sc-10ucg51-0 hfBVJr"})
    inst_details_body = inst_details_table.find('tbody')
    inst_details_rows = inst_details_body.findAll('tr')
    for row in inst_details_rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols if ele])
    for record in data:
        institute_details[record[0]] = record[1]

    # print(institute_details)

    hostel = soup.find('div', attrs={"class": "Styled__OnCampusDiv-sc-1yl1nt-4 ipxyIR"})
    # print(hostel.p.text)
    institute_details[hostel.label.text] = hostel.p.text
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

    num_courses = \
    soup.find('div', attrs={"class": "Styled__FindMoreCourseTitle-sc-1yl1nt-57 egsLwJ"}).span.text.split(' ')[0]
    # print(num_courses)

    intake_month = soup.find_all('div', attrs={"class": "Styled__AdmissionDocumentdiv-sc-1yl1nt-41 dyvnIe"})[
        5].label.text
    # print(intake_month)

    lat_lng_a = soup.find('div', attrs={"class": "Styled__ContactUsMapDiv-sc-1yl1nt-11 byPnsn"})
    lat_lng_url = lat_lng_a.find('a', href=True)['href']
    lat_lng = lat_lng_url.split('/')[-1].split(',')
    # print(lat_lng)

    try:
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
                "main_address": contacts[2].p.text.strip(),
                "latitude": lat_lng[0],
                "longitude": lat_lng[1],
            },
            "institutes_institutedetail": {
                "number_of_programs": ''.join(filter(str.isdigit, num_courses)),
                "campus_size": institute_details.get("Size of Campus in acres"),
                "no_of_international_students": institute_details.get("Total International Students"),
                "intnl_students_percent": institute_details.get("% International Students"),
                "on_campus_hostel": institute_details.get("On campus accommodation"),
                "hostel_fee": ' '.join(institute_details.get("Yearly Hostel & Meals Expense").split(' ')[1:]),
                "hostel_fee_currency_id": institute_details.get("Yearly Hostel & Meals Expense").split(' ')[0],
                "gender_ratio": institute_details.get("Male/Female Ratio"),
                "student_faculty_ratio": institute_details.get("Faculty/Student Ratio"),
                "bachelors_masters_ratio": institute_details.get("UG/PG Course Ratio"),
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
    except KeyError:
        print('key: value not found')
    except ValueError as str_err:
        print('error while parsing string' + str_err.message)
    finally:
        write_json(institute, url.split('/')[-1])


if  __name__ == "__main__":
    universities = ["https://studyabroad.shiksha.com/usa/universities/stanford-university",
                  "https://studyabroad.shiksha.com/usa/universities/arizona-state-university",
                  "https://studyabroad.shiksha.com/usa/universities/the-university-of-texas-at-dallas",
                  "https://studyabroad.shiksha.com/usa/universities/massachusetts-institute-of-technology"]

    for university in universities:
        print('scraping '+university)
        scrape_institute(university)










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
