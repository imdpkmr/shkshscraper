import requests
from bs4 import BeautifulSoup
from shiksha.database import DBQueries


def scrape_courses_url(url):
    urls = []
    response = requests.get(url+"/courses")
    soup = BeautifulSoup(response.content, "html.parser")
    links__ = soup.find_all('a', attrs={"class": "Styled__LinkStyle-sc-19aj422-2 jRTEUB"})
    for l in links__:
        urls.append(l['href'])
        # print(l['href'])
    return urls


if __name__ == "__main__":
    try:
        database = DBQueries()
        conx = database.connect("Institute")
        cursor = conx.cursor()
        url_course_table_query = f"CREATE TABLE IF NOT EXISTS url_courses(course_id INT PRIMARY KEY  AUTO_INCREMENT, institute_id INT, course_rel_url VARCHAR(200), FOREIGN KEY (institute_id) REFERENCES institute_urls(institute_id))"
        cursor.execute(url_course_table_query)
        cursor.execute("select institute_id, institute_url from institute_urls order by institute_id limit 2")
        id_urls = cursor.fetchall()
        queries = []
        for id_url in id_urls:
            id = id_url[0]
            url = id_url[1]
            # print(str(id)+"=>"+url)
            print(f'scraping {url}/courses ')
            url_courses = scrape_courses_url(url)
            # print(url_courses)
            for url_course in url_courses:
                queries.append(f"insert into url_courses(institute_id, course_rel_url) values({id},'{url_course}')")

            for q in queries:
                database.insert_record(conx, q)
                # print(q)
            conx.commit()
    except ConnectionError:
        pass
    finally:
        conx.commit()
        conx.close()