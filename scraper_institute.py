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
            sql += '"' + str(rowdict[keys[i]]) + '"'
        else:
            sql += str(rowdict[keys[i]])
        if (i < dictsize - 1):
            sql += ', '
    columns = ', '.join(keys)
    query = "insert into " + str(tablename) + " (" + columns + ") values(" + sql + ")"
    query = query.replace("None", "null")
    # print(query) # for demo purposes we do this
    return (query)  # in real code we do this


def scrape_institute(url, id=0):
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
    except ValueError:
        pass

    contact_details = {}
    try:
        contacts = soup.find_all('div', attrs={"class": "Styled__ContactUsDiv-sc-1yl1nt-10 cNAOeO"})
        # for c in contacts:
        #     print(c)
        contact_details.update({
            "website": contacts[3].p.a['href'],
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
        # institute_details[hostel.label.text] = hostel.p.text
        institute_details.update({
            "hostel_fee": ' '.join(hostel.p.text.split(' ')[1:]),
            "hostel_fee_currency_id": hostel.p.text.split(' ')[0],
        })
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
    intake = {}
    try:
        intake_month = soup.find_all('div', attrs={"class": "Styled__AdmissionDocumentdiv-sc-1yl1nt-41 dyvnIe"})[
            5].label.text
        pass
        # print(intake_month)
        rankings = soup.find_all('div', attrs={"class": "Styled__RankingListBox-sc-132amsi-9 iVoSAn"})
        ranking = rankings[0].find_all('div')
        rank.update({"ranking_authority_id": ranking[0].text,
                     "ranking_type_id": ranking[2].label.text,
                     "rank": ''.join(filter(str.isdigit, ranking[2].p.strong.text))})
        intake_month = soup.find_all('div', attrs={"class": "Styled__AdmissionDocumentdiv-sc-1yl1nt-41 dyvnIe"})[
            5].label.text
        intake.update({
            "intake_month": intake_month,
        })
        # print(intake_month)

    except IndexError:
        pass

    # for r in rank:
    #     print(r.text)
    # print(rank[0].text)
    # print(rank[2].label.text)
    # print(rank[2].p.strong.text)


    inst_contact = {}
    try:
        lat_lng_a = soup.find('div', attrs={"class": "Styled__ContactUsMapDiv-sc-1yl1nt-11 byPnsn"})
        lat_lng_url = lat_lng_a.find('a', href=True)['href']
        # lat_lng = lat_lng_url.split('/')[-1].split(',')
        inst_contact.update({"lat": lat_lng_url.split('/')[-1].split(',')[0]})
        inst_contact.update({"lng": lat_lng_url.split('/')[-1].split(',')[1]})
    except AttributeError as aerr:
        print(aerr)
    except IndexError as err:
        pass
    # print(lat_lng)

    try:
        institute = {
            "institute_institute": {
                "url":url,
                "name": institute.get("name"),
                "id": id,
                "short_name": None,
                "established_year": institute.get("established_year"),
                "institute_type": institute.get("institute_type"),
                "country_id": None,
                "state_id": None,
                "city_id": None,
                "brochure": None,
            },
            "institutes_institutecontactdetail": {
                "id": id,
                "website": contact_details.get("website"),
                "phone_nos": contact_details.get("phone_nos"),
                "fax": contact_details.get("fax"),
                "email_address": contact_details.get("email_address"),
                "main_address": contact_details.get("main_address"),
                "latitude": inst_contact.get("lat"),
                "longitude": inst_contact.get("lng"),
            },
            "institutes_institutedetail": {
                "id": id,
                "number_of_programs": institute_details.get("number_of_programs"),
                "campus_size": institute_details.get("Size of Campus in acres"),
                "no_of_international_students": institute_details.get("Total International Students"),
                "intnl_students_percent": institute_details.get("% International Students"),
                "on_campus_hostel": institute_details.get("On campus accommodation"),
                "hostel_fee": institute_details.get("hostel_fee"),
                "hostel_fee_currency_id": institute_details.get("hostel_fee_currency_id"),
                "gender_ratio": institute_details.get("Male/Female Ratio"),
                "student_faculty_ratio": institute_details.get("Faculty/Student Ratio"),
                "bachelors_masters_ratio": institute_details.get("UG/PG Course Ratio"),
            },
            "institutes_instituteranking": {
                "id": id,
                "ranking_authority_id": rank.get("ranking_authority_id"),
                "ranking_type_id": rank.get("ranking_type_id"),
                "rank": rank.get("rank"),
            },
            "institute_coursefee": {
                "id": id,
                "min_fee": fee.get("min_fee"),
                "max_fee": fee.get("max_fee"),
                "currency_id": fee.get("currency_id"),
            },
            "institutes_institute_intake": {
                "id": id,
                "intake_id": intake.get("intake_month"),
            }
        }
        # print(institute["institutes_institutecontactdetail"])
        insert_queries.append(ins_query_maker("institute_institute", institute["institute_institute"]))
        insert_queries.append(ins_query_maker("institutes_institutecontactdetail", institute["institutes_institutecontactdetail"]))
        insert_queries.append(ins_query_maker("institutes_institutedetail", institute["institutes_institutedetail"]))
        insert_queries.append(ins_query_maker("institutes_instituteranking", institute["institutes_instituteranking"]))
        insert_queries.append(ins_query_maker("institute_coursefee", institute["institute_coursefee"]))
        insert_queries.append(ins_query_maker("institutes_institute_intake", institute["institutes_institute_intake"]))

        return insert_queries
    except KeyError:
        print('key: value not found')
    except ValueError as str_err:
        print('error while parsing string' + str_err.message)
    finally:
        pass
        # write_json(institute, url.split('/')[-1])


if __name__ == "__main__":
    # universities = ["https://studyabroad.shiksha.com/usa/universities/stanford-university",
    #                 "https://studyabroad.shiksha.com/usa/universities/arizona-state-university",
    #                 "https://studyabroad.shiksha.com/usa/universities/the-university-of-texas-at-dallas",
    #                 "https://studyabroad.shiksha.com/usa/universities/massachusetts-institute-of-technology",
    #                 "https://studyabroad.shiksha.com/usa/universities/california-state-university-los-angeles-campus"]

    database = DBQueries()
    queries = [
        f"CREATE TABLE IF NOT EXISTS institute_institute( id INT PRIMARY KEY, url VARCHAR(200) UNIQUE NOT NULL,name VARCHAR(100), short_name VARCHAR(50), established_year VARCHAR(5), institute_type VARCHAR(200), country_id VARCHAR(22), state_id VARCHAR(22), city_id VARCHAR(22), brochure VARCHAR(22))",
        f"CREATE TABLE IF NOT EXISTS institute_coursefee(id INT, min_fee VARCHAR(20), max_fee VARCHAR(20), currency_id VARCHAR(20), FOREIGN KEY (id) REFERENCES institute_institute(id))",
        f"CREATE TABLE IF NOT EXISTS institutes_institutecontactdetail(id INT, website VARCHAR(500), phone_nos VARCHAR(100), fax VARCHAR(15), email_address VARCHAR(50), main_address VARCHAR(200), latitude VARCHAR(50), longitude VARCHAR(50), FOREIGN KEY (id) REFERENCES institute_institute(id))" ,
        f"CREATE TABLE IF NOT EXISTS institutes_institutedetail(id INT, number_of_programs VARCHAR(20), campus_size VARCHAR(20), no_of_international_students VARCHAR(20), intnl_students_percent VARCHAR(20), on_campus_hostel VARCHAR(20), hostel_fee VARCHAR(20), hostel_fee_currency_id VARCHAR(20), gender_ratio VARCHAR(20), student_faculty_ratio VARCHAR(20), bachelors_masters_ratio VARCHAR(20), FOREIGN KEY (id) REFERENCES institute_institute(id))",
        f"CREATE TABLE IF NOT EXISTS institutes_instituteranking(id INT, ranking_authority_id VARCHAR(100), ranking_type_id VARCHAR(100), rank VARCHAR(20), FOREIGN KEY (id) REFERENCES institute_institute(id))",
        f"CREATE TABLE IF NOT EXISTS institutes_institute_intake(id INT, intake_id VARCHAR(20), FOREIGN KEY (id) REFERENCES institute_institute(id))"
    ]


    try:
        conx = database.connect("Institute")
        for query in queries:
            database._create_table(conx, query)
        cursor = conx.cursor()
        cursor.execute("select id from institute_institute")
        try:
            id = cursor.fetchall()[-1][0]
        except IndexError:
            id = 1
        # print(id)
        cursor.execute("SELECT DISTINCT institute_url FROM institute_urls")
        universities = cursor.fetchall()
        print(len(universities))
        cursor.close()

        q = scrape_institute("https://studyabroad.shiksha.com/usa/universities/texas-tech-university")

        for uni in universities:
            university = str(uni[0])
            print('scraping ' + university)
            id = id + 1
            insert_queries = scrape_institute(university, id)
            for query in insert_queries:
                database.insert_record(conx, query)
                # print(query)
    except ConnectionError:
        pass
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
