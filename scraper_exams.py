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

    exams = {}
    try:
        pass
    except IndexError:
        pass
    except TypeError:
        pass


    try:
        exam = {
            "institutes_instituteexamrelation": {
                "exam": None
            }
        }
        insert_queries.append(ins_query_maker("institutes_instituteexamrelation", exam["institutes_instituteexamrelation"]))
        return  insert_queries
    except IndexError:
        pass
    finally:
        write_json(exams, url.split('/')[-1])

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
    create_queries = [f"CREATE TABLE insinstitutes_institutecourse(department VARCHAR(100), degree_id VARCHAR(100), stream_id VARCHAR(100), name VARCHAR(100), level_id VARCHAR(100))"]
    for query in create_queries:
        database._create_table(conx, query)
    try:
        for url in urls:
            print('scraping ', url)
            insert_queries = scrape_courses(url)
            # for query in insert_queries:
            #     database.insert_record(conx, query)
    except ConnectionError:
        pass
    finally:
        conx.commit()
