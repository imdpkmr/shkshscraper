import json

import requests
from bs4 import BeautifulSoup

from shiksha.database import DBQueries

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
    query = query.replace("None", "null")
    # print(query) # for demo purposes we do this
    return (query)  # in real code we do this

def write_json(institute, university_name=""):
    json_object = json.dumps(institute, indent=2)
    filename = "json/" + university_name + "_data.json"
    with open(filename, "w") as outfile:
        outfile.write(json_object)

def scrape_courses( url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    insert_queries = []

    coursedetails = {}
    try:
        course_details_ = soup.find('table', attrs={"class": "Styled__TableStyle-sc-10ucg51-0 lfnXDf"})
        course_details__ = course_details_.find_all("td")
        # for coursed in course_details__:
        #     print(coursed.text)
        coursedetails.update({
            "course_duration": course_details__[1].text.split(' ')[0],
            "duration_type": course_details__[1].text.split(' ')[-1],
            "level_id": course_details__[3].text,
        })
        # print(course_details__[1].text.split(' ')[0], course_details__[1].text.split(' ')[-1], course_details__[3].text)
    except IndexError:
        pass

    try:
        courses_ = soup.find('div', attrs={"class": "Styled__WidgetHeading-opouq6-1 bSjtKj"})
        for _ in courses_.find_all('div'):
            _.decompose()
        # print(courses_.text)

        fees__ = soup.find('table', attrs={"class": "Styled__TableStyle-sc-10ucg51-0 vXiFr"})
        fees_ = fees__.find_all('td')
        # for _ in fees_:
        #     print(_.text)
        coursedetails.update({
            "name": courses_.text,
            "fee_currency_id": fees_[1].text.split(' ')[0],
            "fee": fees_[1].text.split(' ')[-1],
        })
    except IndexError:
        pass
    except TypeError:
        pass


    try:
        courses = {
            "insinstitutes_institutecourse": {
                "department": "NA",
                "degree_id": "Manual",
                "stream_id": "Manual",
                "name": coursedetails.get("name"),
                "level_id": coursedetails.get("level_id"),
            },
            "institutes_institutecoursecommondetail": {
                "mode": "NA",
                "course_duration": coursedetails.get("course_duration"),
                "duration_type": coursedetails.get("duration_type"),
                "fee": coursedetails.get("fee"),
                "fee_currency_id": coursedetails.get("fee_currency_id"),
            },
            "institutes_institutecourse_specialization": "Manual",
        }

        insert_queries.append(ins_query_maker("insinstitutes_institutecourse", courses["insinstitutes_institutecourse"]))
        insert_queries.append(ins_query_maker("institutes_institutecoursecommondetail", courses["institutes_institutecoursecommondetail"]))
        insert_queries.append(f"INSERT INTO institutes_institutecourse_specialization(specialization) values('{courses.get('institutes_institutecourse_specialization')}')")

        return  insert_queries
    except IndexError:
        pass
    finally:
        write_json(courses, url.split('/')[-1])

if __name__ == "__main__":
    urls = [
        "https://studyabroad.shiksha.com/uk/universities/university-of-oxford/msc-in-computer-science",
        "https://studyabroad.shiksha.com/usa/universities/harvard-university/mba",
        "https://studyabroad.shiksha.com/uk/universities/university-of-cambridge/master-of-business-administration",
        "https://studyabroad.shiksha.com/usa/universities/stanford-university/master-of-business-administration",
        "https://studyabroad.shiksha.com/usa/universities/harvard-university/masters-in-computer-science"
    ]

    database = DBQueries()
    conx = database.connect("Courses")
    # create_queries = [
    #     f"CREATE TABLE insinstitutes_institutecourse(department VARCHAR(100), degree_id VARCHAR(100), stream_id VARCHAR(100), name VARCHAR(100), level_id VARCHAR(100))",
    #     f"CREATE TABLE institutes_institutecoursecommondetail(mode VARCHAR(100), course_duration VARCHAR(100), duration_type VARCHAR(100), fee VARCHAR(100), fee_currency_id VARCHAR(100))",
    #     f"CREATE TABLE institutes_institutecourse_specialization(specialization VARCHAR(100))"
    # ]
    # for query in create_queries:
    #     database._create_table(conx, query)
    try:
        for url in urls:
            print('scraping ', url)
            insert_queries = scrape_courses(url)
            for query in insert_queries:
                database.insert_record(conx, query)
    except ConnectionError:
        pass
    finally:
        conx.commit()
