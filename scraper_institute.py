import json

import requests
from bs4 import BeautifulSoup

from shiksha.database import DBQueries


def write_json(institute, university_name=""):
    json_object = json.dumps(institute, indent=2)
    filename = "json/" + university_name + "_data.json"
    with open(filename, "w") as outfile:
        outfile.write(json_object)


def ins_query_maker(tablename, rowdict):
    keys = tuple(rowdict)
    dictsize = len(rowdict)
    sql = ''
    for i in range(dictsize):
        if (type(rowdict[keys[i]]).__name__ == 'str'):
            sql += "'" + str(rowdict[keys[i]]) + "'"
        else:
            sql += str(rowdict[keys[i]])
        if (i < dictsize - 1):
            sql += ', '
    columns = ', '.join(keys)
    query = "insert into " + str(tablename) + " (" + columns + ") values(" + sql + ")"
    # print(query) # for demo purposes we do this
    return (query)  # in real code we do this


def scrape_institute(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    insert_queries = []

    institute = {}
    try:
        title = soup.find('h1', attrs={"class": "H1-sc-1225uyb-0 KmIux"}).text
        # print(title)
        _, institute_type, established_year_ = soup.find('div', attrs={
            "class": "Styled__UnivLinks-sc-132amsi-4 gXZkCE"}).text.split('|')
        # print(institute_type)
        established_year = ''.join(filter(str.isdigit, established_year_))
        # print(established_year)
        institute.update({
            "name": title,
            "established_year": established_year,
            "institute_type": institute_type,
        })
    except AttributeError:
        pass
    except IndexError:
        pass

    contact_details = {}
    try:
        contacts = soup.find_all('div', attrs={"class": "Styled__ContactUsDiv-sc-1yl1nt-10 cNAOeO"})
        contact_details.update({
            "website": contacts[3].p.text,
            "phone_nos": contacts[1].p.text,
            "fax": None,
            "email_address": contacts[0].p.text,
            "main_address": contacts[2].p.text.strip(),
        })
    except IndexError:
        pass

    data = []
    institute_details = {}
    try:
        inst_details_table = soup.find('table', attrs={"class": "Styled__TableStyle-sc-10ucg51-0 hfBVJr"})
        inst_details_body = inst_details_table.find('tbody')
        inst_details_rows = inst_details_body.findAll('tr')
        for row in inst_details_rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            data.append([ele for ele in cols if ele])
        for record in data:
            institute_details[record[0]] = record[1]
        num_courses = \
        soup.find('div', attrs={"class": "Styled__FindMoreCourseTitle-sc-1yl1nt-57 egsLwJ"}).span.text.split(' ')[0]
        number_of_programs = ''.join(filter(str.isdigit, num_courses))
        institute_details.update({"number_of_programs": number_of_programs})
        # print(num_courses)
        hostel = soup.find('div', attrs={"class": "Styled__OnCampusDiv-sc-1yl1nt-4 ipxyIR"})
        institute_details[hostel.label.text] = hostel.p.text
        # print(hostel.p.text)
    except IndexError:
        pass
    except AttributeError:
        pass

    # print(institute_details)

    fee = {}
    try:
        app_fee = soup.find('td', string="Application fees")
        application_fees = app_fee.find_next_sibling('td').text.split(' ')
        fee.update({"currency_id": application_fees[0],
                    "min_fee": application_fees[1],
                    "max_fee": application_fees[3]})
    except IndexError:
        pass

    rank = {}
    try:
        rankings = soup.find_all('div', attrs={"class": "Styled__RankingListBox-sc-132amsi-9 iVoSAn"})
        ranking = rankings[0].find_all('div')
        rank.update({"ranking_authority_id": ranking[0].text,
                     "ranking_type_id": ranking[2].label.text,
                     "rank": ''.join(filter(str.isdigit, ranking[2].p.strong.text))})

    except IndexError:
        pass

    # for r in rank:
    #     print(r.text)
    # print(rank[0].text)
    # print(rank[2].label.text)
    # print(rank[2].p.strong.text)

    intake_month = soup.find_all('div', attrs={"class": "Styled__AdmissionDocumentdiv-sc-1yl1nt-41 dyvnIe"})[
        5].label.text
    # print(intake_month)

    inst_contact = {}
    try:
        lat_lng_a = soup.find('div', attrs={"class": "Styled__ContactUsMapDiv-sc-1yl1nt-11 byPnsn"})
        lat_lng_url = lat_lng_a.find('a', href=True)['href']
        # lat_lng = lat_lng_url.split('/')[-1].split(',')
        inst_contact.update({"lat": lat_lng_url.split('/')[-1].split(',')[0]})
        inst_contact.update({"lng": lat_lng_url.split('/')[-1].split(',')[1]})
    except AttributeError as aerr:
        print(aerr)
    # print(lat_lng)

    try:
        institute = {
            "institute_institute": {
                "name": institute.get("name"),
                "id": None,
                "short_name": None,
                "established_year": institute.get("established_year"),
                "institute_type": institute.get("institute_type"),
                "country_id": None,
                "state_id": None,
                "city_id": None,
                "brochure": None,
            },
            "institutes_institutecontactdetail": {
                "website": contact_details.get("website"),
                "phone_nos": contact_details.get("phone_nos"),
                "fax": contact_details.get("fax"),
                "email_address": contact_details.get("email_address"),
                "main_address": contact_details.get("main_address"),
                "latitude": inst_contact.get("lat"),
                "longitude": inst_contact.get("lng"),
            },
            "institutes_institutedetail": {
                "number_of_programs": institute_details.get("number_of_programs"),
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
                "ranking_authority_id": rank.get("ranking_authority_id"),
                "ranking_type_id": rank.get("ranking_type_id"),
                "rank": rank.get("rank"),
            },
            "institute_coursefee": {
                "min_fee": fee.get("min_fee"),
                "max_fee": fee.get("max_fee"),
                "currency_id": fee.get("currency_id"),
            },
            "institutes_institute_intake": {
                "intake_id": intake_month,
            }
        }
        # print(institute["institutes_instituteranking"])
        insert_queries.append(ins_query_maker("institute_institute", institute["institute_institute"]))
        insert_queries.append(
            ins_query_maker("institutes_institutecontactdetail", institute["institutes_institutecontactdetail"]))
        insert_queries.append(ins_query_maker("institutes_institutedetail", institute["institutes_institutedetail"]))
        insert_queries.append(ins_query_maker("institutes_instituteranking", institute["institutes_instituteranking"]))
        insert_queries.append(ins_query_maker("institute_coursefee", institute["institute_coursefee"]))
        insert_queries.append(f"insert into institutes_institute_intake(intake_id) values('{institute.get('institutes_institute_intake',{}).get('intake_id')}')")

        return insert_queries
    except KeyError:
        print('key: value not found')
    except ValueError as str_err:
        print('error while parsing string' + str_err.message)
    finally:
        write_json(institute, url.split('/')[-1])


if __name__ == "__main__":
    universities = ["https://studyabroad.shiksha.com/usa/universities/stanford-university",
                    "https://studyabroad.shiksha.com/usa/universities/arizona-state-university",
                    "https://studyabroad.shiksha.com/usa/universities/the-university-of-texas-at-dallas",
                    "https://studyabroad.shiksha.com/usa/universities/massachusetts-institute-of-technology",
                    "https://studyabroad.shiksha.com/usa/universities/california-state-university-los-angeles-campus"]

    database = DBQueries()
    conx = database.connect()
    try:
        for university in universities:
            print('scraping ' + university)
            insert_queries = scrape_institute(university)
            for query in insert_queries:
                query = query.replace("None", "null")
                database.insert_record(conx, query)
                # print(query)
    finally:
        pass
    conx.commit()

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
