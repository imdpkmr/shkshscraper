import requests
from bs4 import BeautifulSoup
import math

# Writing to an excel  sheet using Python  Workbook is created
# wb = Workbook()
# add_sheet is used to create sheet.
# sheet1 = wb.add_sheet('Sheet 1') # sheet1.write(1, 0, 'ISBT DEHRADUN') # wb.save('xlwt example.xls')
from database import DBQueries


def scrape_url(p_url):
    rspn = requests.get(p_url)
    soup_pages = BeautifulSoup(rspn.content, "html.parser")
    pages = soup_pages.find('div', attrs={"class": "pagination clearwidth"}).p.text.split(' ')[-2]
    number_pages = math.ceil(int(pages)/20)
    # print(number_pages)
    urls = []
    for page in range(number_pages):
        page_url = p_url+"-"+str(page)
        print(page_url)
        response = requests.get(page_url)
        soup = BeautifulSoup(response.content, "html.parser")
        links = soup.find_all('div', attrs={"class": "tuple-title"})
        # print([link.a['href'] for link in links])
        urls_ = [link.a['href'] for link in links]
        for url in urls_:
            if(len(str(url).split('/')) == 6):
                urls.append(url)

    return urls

if __name__ == "__main__":
    urls = ["https://studyabroad.shiksha.com/be-btech-in-abroad-dc11510",
            "https://studyabroad.shiksha.com/mba-in-abroad-dc11508",
            "https://studyabroad.shiksha.com/ms-in-abroad-dc11509"]
    # "https://studyabroad.shiksha.com/certificate-diploma-in-engineering-in-abroad-cl1240",
    # "https://studyabroad.shiksha.com/certificate-diploma-in-business-in-abroad-cl1239",
    # "https://studyabroad.shiksha.com/certificate-diploma-in-computers-in-abroad-cl1241",
    # "https://studyabroad.shiksha.com/bachelors-in-media-courses-in-abroad-sl1325",
    # "https://studyabroad.shiksha.com/bachelors-in-fashion-design-courses-in-abroad-sl1331",
    # "https://studyabroad.shiksha.com/bachelors-of-business-in-abroad-cl1239",
    # "https://studyabroad.shiksha.com/ms-in-aerospace-engineering-from-abroad-ds11509269",
    # "https://studyabroad.shiksha.com/ms-in-civil-engineering-from-abroad-ds11509264",
    # "https://studyabroad.shiksha.com/mba-in-accounting-from-abroad-ds11508247",
    # "https://studyabroad.shiksha.com/masters-in-journalism-courses-in-abroad-sl1328",
    # "https://studyabroad.shiksha.com/mba-in-hospitality-from-abroad-ds11508256",
    try:
        database = DBQueries()
        conx = database.connect("Institute")
        create_queries = f"CREATE TABLE IF NOT EXISTS institute_urls(institute_id INT PRIMARY KEY AUTO_INCREMENT, institute_url VARCHAR(500) UNIQUE )"
        database._create_table(conx, create_queries)

        for url in urls:
            print('scraping ', url)
            urls = scrape_url(url)
            inst_urls = list(database.get_records(conx, "select institute_url from institute_urls"))
            for u in urls:
                if u not in inst_urls:
                    query = f"INSERT INTO institute_urls(institute_url) VALUES('{u}')"
                    # print(query)
                    database.insert_record(conx, query)
            conx.commit()
    except Exception as e:
        print("exception ", e)
    finally:
        conx.commit()
        conx.close()
