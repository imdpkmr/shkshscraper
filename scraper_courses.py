import json

import requests
from bs4 import BeautifulSoup

from database import DBQueries

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

def scrape_courses( course_id, institute_id, url):
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
    except AttributeError:
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
    except AttributeError:
        pass


    try:
        courses = {
            "institutes_institutecourse": {
                "institute_id":institute_id,
                "course_id":course_id,
                "department": "NA",
                "degree_id": "Manual",
                "stream_id": "Manual",
                "name": coursedetails.get("name"),
                "level_id": coursedetails.get("level_id"),
            },
            "institutes_institutecourse_commondetail": {
                "institute_id":institute_id,
                "course_id":course_id,
                "mode": "NA",
                "course_duration": coursedetails.get("course_duration"),
                "duration_type": coursedetails.get("duration_type"),
                "fee": coursedetails.get("fee"),
                "fee_currency_id": coursedetails.get("fee_currency_id"),
            },
            "institutes_institutecourse_specialization": "Manual",
        }

        insert_queries.append(ins_query_maker("institutes_institutecourse", courses["institutes_institutecourse"]))
        insert_queries.append(ins_query_maker("institutes_institutecourse_commondetail", courses["institutes_institutecourse_commondetail"]))
        insert_queries.append(f"INSERT INTO institutes_institutecourse_specialization(institute_id,course_id, specialization) values({institute_id},{course_id},'{courses.get('institutes_institutecourse_specialization')}')")

        return  insert_queries
    except IndexError:
        pass
    finally:
        pass
        # write_json(courses, url.split('/')[-1])

if __name__ == "__main__":
    # urls = [
    #     "https://studyabroad.shiksha.com/uk/universities/university-of-oxford/msc-in-computer-science",
    #     "https://studyabroad.shiksha.com/usa/universities/harvard-university/mba",
    #     "https://studyabroad.shiksha.com/uk/universities/university-of-cambridge/master-of-business-administration",
    #     "https://studyabroad.shiksha.com/usa/universities/stanford-university/master-of-business-administration",
    #     "https://studyabroad.shiksha.com/usa/universities/harvard-university/masters-in-computer-science"
    # ]

    create_queries = [
        f"CREATE TABLE IF NOT EXISTS institutes_institutecourse(institute_id INT, course_id INT,  department VARCHAR(100), degree_id VARCHAR(100), stream_id VARCHAR(100), name VARCHAR(100), level_id VARCHAR(100),FOREIGN KEY (course_id) REFERENCES url_courses(course_id), FOREIGN KEY (institute_id) REFERENCES institute_urls(institute_id))",
        f"CREATE TABLE IF NOT EXISTS institutes_institutecourse_commondetail(institute_id INT,course_id INT, mode VARCHAR(100), course_duration VARCHAR(100), duration_type VARCHAR(100), fee VARCHAR(100), fee_currency_id VARCHAR(100), FOREIGN KEY (institute_id) REFERENCES institute_urls(institute_id), FOREIGN KEY (course_id) REFERENCES url_courses(course_id))",
        f"CREATE TABLE IF NOT EXISTS institutes_institutecourse_specialization(institute_id INT, course_id INT,  specialization VARCHAR(100), FOREIGN KEY (institute_id) REFERENCES institute_urls(institute_id), FOREIGN KEY (course_id) REFERENCES url_courses(course_id))"
    ]
    try:
        database = DBQueries()
        conx = database.connect("Institute")
        for query in create_queries:
            database._create_table(conx, query)
        cid_iid_rurls = database.get_records(conx, f"select course_id, institute_id, course_rel_url from url_courses where course_id  > 15477054 order by institute_id, course_id ")
        for cid_iid_rurl in cid_iid_rurls:
            course_id = cid_iid_rurl[0]
            institute_id = cid_iid_rurl[1]
            rurl = cid_iid_rurl[2]
            url = "https://studyabroad.shiksha.com" + rurl
            print(institute_id, course_id, url)
            # print(str(id)+"=>"+rurl)
            # for url in urls:
            #     print('scraping ', url)
            insert_queries = scrape_courses(course_id, institute_id, url)
            for query in insert_queries:
                database.insert_record(conx, query)
            conx.commit()
    except ConnectionError:
        pass
    except OSError:
        pass
    finally:
        conx.commit()
        conx.close()
