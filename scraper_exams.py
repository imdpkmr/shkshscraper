import json
import re

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
    filename = "out_files/json/exams/" + university_name + "_data.json"
    with open(filename, "w") as outfile:
        outfile.write(json_object)

def scrape_exams(institute_id, course_id, url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    insert_queries = []

    exams_entrance = {}
    try:
        exams__ = soup.find_all('table', attrs={"class": "Styled__TableStyle-sc-10ucg51-0 lfnXDf"})[1]
        # print(exams__.text)
        exams_ = exams__.find_all('tr')
        for _ in exams_:
            if _.find(text=re.compile("Exams")):
                exams = _
                break
        exam = exams.find_all('div', attrs={"class": "Styled__EntryReqDetails-sc-14wej5r-4 jcAfxi"})
        for eexam in exam:
            # print(eexam.label.text)
            # print(eexam.span.text)
            exams_entrance.update({
                eexam.label.text: eexam.span.text,
            })
        # for link in links:
        #     if link.find(text=re.compile("Edit")):
        #         thelink = link
        #         break
    except IndexError:
        pass
    except TypeError:
        pass


    try:
        exam = {
            "institutes_instituteexamrelation": {
                "institute_id": institute_id,
                "course_id": course_id,
                "toefl": exams_entrance.get("TOEFL :"),
                "ielts": exams_entrance.get("IELTS :"),
                "pte": exams_entrance.get("PTE :"),
                "gre": exams_entrance.get("GRE :"),
                "gmat": exams_entrance.get("GMAT :"),
            }
        }
        insert_queries.append(ins_query_maker("institutes_instituteexamrelation", exam["institutes_instituteexamrelation"]))
        return insert_queries
    except IndexError:
        pass
    finally:
        pass
        # write_json(exams, url.split('/')[-1])

if __name__ == "__main__":
    # urls = [
    #     "https://studyabroad.shiksha.com/uk/universities/university-of-oxford/msc-in-computer-science",
    #     "https://studyabroad.shiksha.com/usa/universities/harvard-university/mba",
    #     "https://studyabroad.shiksha.com/uk/universities/university-of-cambridge/master-of-business-administration",
    #     "https://studyabroad.shiksha.com/usa/universities/stanford-university/master-of-business-administration",
    #     "https://studyabroad.shiksha.com/usa/universities/harvard-university/masters-in-computer-science"
    # ]

    create_queries = f"CREATE TABLE IF NOT EXISTS institutes_instituteexamrelation(institute_id INT, course_id INT, toefl VARCHAR(100), ielts VARCHAR(100), pte VARCHAR(100), gre VARCHAR(100), gmat VARCHAR(100), FOREIGN KEY (institute_id) REFERENCES institute_urls(institute_id), FOREIGN KEY (course_id) REFERENCES url_courses(course_id))"
    try:
        database = DBQueries()
        conx = database.connect("Institute")
        database._create_table(conx, create_queries)
        cid_iid_rurls = database.get_records(conx, f"select course_id, institute_id, course_rel_url from url_courses order by course_id limit 2")
        for cid_iid_rurl in cid_iid_rurls:
            course_id = cid_iid_rurl[0]
            institute_id = cid_iid_rurl[1]
            rurl = cid_iid_rurl[2]
            url = "https://studyabroad.shiksha.com" + rurl
            insert_queries = scrape_exams(institute_id, course_id, url)
            for query in insert_queries:
                database.insert_record(conx, query)
            conx.commit()
    except ConnectionError:
        pass
    finally:
        conx.commit()
