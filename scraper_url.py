import requests
from bs4 import BeautifulSoup
import xlwt
from xlwt import Workbook

# Writing to an excel  sheet using Python  Workbook is created
# wb = Workbook()
# add_sheet is used to create sheet.
# sheet1 = wb.add_sheet('Sheet 1') # sheet1.write(1, 0, 'ISBT DEHRADUN') # wb.save('xlwt example.xls')

def scrape_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    wb = Workbook()
    sheet1 = wb.add_sheet('Sheet ')
    links = soup.find_all('a', attrs={"class": "tuple-sub-title"}, href=True)
    for index, value in enumerate(links):
        sheet1.write(index+1, 0, value['href'])
        # print(_['href'])
    wb.save('out_files/'+url.split('/')[-1]+'urls.xls')

if __name__ == "__main__":
    urls = [
        "https://studyabroad.shiksha.com/usa/be-btech-colleges-dc",
        "https://studyabroad.shiksha.com/usa/mba-colleges-dc",
        "https://studyabroad.shiksha.com/usa/be-btech-colleges-dc",
        "https://studyabroad.shiksha.com/usa/bba-colleges-dc",
        "https://studyabroad.shiksha.com/usa/bsc-colleges-dc"
    ]

    for url in urls:
        print('scraping ', url)
        scrape_url(url)
