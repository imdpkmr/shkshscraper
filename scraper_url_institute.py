import requests
from bs4 import BeautifulSoup
import math

# Writing to an excel  sheet using Python  Workbook is created
# wb = Workbook()
# add_sheet is used to create sheet.
# sheet1 = wb.add_sheet('Sheet 1') # sheet1.write(1, 0, 'ISBT DEHRADUN') # wb.save('xlwt example.xls')
from shiksha.database import DBQueries


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
    urls = ["https://studyabroad.shiksha.com/usa/be-btech-colleges-dc",
        "https://studyabroad.shiksha.com/usa/mba-colleges-dc",
        "https://studyabroad.shiksha.com/usa/be-btech-colleges-dc",
        "https://studyabroad.shiksha.com/usa/bba-colleges-dc",
        "https://studyabroad.shiksha.com/usa/bsc-colleges-dc",
        "https://studyabroad.shiksha.com/usa/march-colleges-dc",
        "https://studyabroad.shiksha.com/usa/mim-colleges-dc",
        "https://studyabroad.shiksha.com/usa/ma-colleges-dc",
        "https://studyabroad.shiksha.com/usa/mem-colleges-dc"
    ]
    database = DBQueries()
    conx = database.connect("Institute")
    create_queries = f"CREATE TABLE IF NOT EXISTS institute_urls(id INT PRIMARY KEY AUTO_INCREMENT, institute_url VARCHAR(500))"
    database._create_table(conx, create_queries)

    for url in urls:
        print('scraping ', url)
        urls = scrape_url(url)
        for u in urls:
            pass
            query = f"INSERT INTO institute_urls(institute_url) VALUES('{u}')"
            database.insert_record(conx, query)

    conx.commit()
