import json

import requests
from bs4 import BeautifulSoup

from database import DBQueries


def write_json(institute_json, university_name=""):
    json_object = json.dumps(institute_json, indent=2)
    filename = "out_files/json/" + university_name + "_data.json"
    with open(filename, "w") as outfile:
        outfile.write(json_object)


def scrape_institute(url, id):
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
        num_courses = soup.find('div', attrs={"class": "Styled__FindMoreCourseTitle-sc-1yl1nt-57 egsLwJ"}).span.text.split(' ')[0]
        number_of_programs = ''.join(filter(str.isdigit, num_courses))
        institute_details.update({"number_of_programs": number_of_programs})
        # print(num_courses)
        hostel = institute_details.get("Yearly Hostel & Meals Expense")
        if hostel is None:
            institute_details.update({
                "on_campus_hostel": "No",
            })
        else:
            # print(hostel)
            institute_details.update({
                "on_campus_hostel": "Yes",
                "hostel_fee": ' '.join(hostel.split(' ')[1:]),
                "hostel_fee_currency_id": hostel.split(' ')[0],
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
    except AttributeError:
        pass

    rank_uni = {}
    try:
        rankings__ = soup.find_all('div', attrs={"class":"Styled__RankingListBox-sc-132amsi-9 iVoSAn"})
        for rankings_ in rankings__:
            rankings = rankings_.find_all('div')
            rank_name = rankings[0].text
            rank = rankings[2].p.text
            # print("rank name ->", rank_name)
            # print("rank ->", rank, "=>")
            if "QS" in rank_name:
                rank_uni.update({"qs_ranking_year": rank_name.split(" ")[-2],
                             "qs_ranking": rank.split('#')[-1]})
            if "Times Higher Education" in rank_name:
                rank_uni.update({"times_higher_education_year": rank_name.split(' ')[-2],
                             "times_higher_education": rank.split('#')[-1]})
            if "U.S. News" in rank_name:
                rank_uni.update({"usnews_year": rank_name.split(' ')[-2],
                             "usnews": rank.split('#')[-1]})

            for r in rankings:
                pass
        # print(rank_uni)
    except IndexError:
        pass
    except AttributeError:
        pass

    intake_months = {}
    try:
        intake_month__ = soup.find_all('table', attrs={"class": "Styled__TableStyle-sc-10ucg51-0 lfnXDf"})[-2]
        intake_month_ = intake_month__.find_all('tr')[-1]
        intake_month = intake_month_.find_all('td')
        if(intake_month[0].text == "Intake Season & Deadlines"):
            intakes = intake_month[1].find_all('div')
            intake_index = 0
            im = "intake_month"
            for intake in intakes:
                # print(intake.text)
                intake_months.update({im: intake.text.split(' ')[-2]})
                intake_index+=1
                im = "intake_month_"+str(intake_index)
        # print(intake_months)
    except IndexError:
        pass
    except AttributeError:
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

    logo = {}
    try:
        logo_link_ = soup.find('img', attrs={"class":"Styled__ImageDiv-sc-5p2r35-0 gYjxkS"})
        logo_link = logo_link_['src']
        # print(logo_link_)
        logo.update({"logo":logo_link})
    except AttributeError:
        pass
    except IndexError:
        pass

    try:
        institute_dict = {
            institute.get("name") : {
                "name_of_the_university": institute.get("name"),
                "short_name": None,#do we need to make it or get from the name of the insti
                "establishment_year": institute.get("established_year"),
                "institute_type": institute.get("institute_type"),
                "country": None,#need to use API to get next three fields as per the excel sheet, else this info can be extracted from the page itself
                "state": None,
                "city": None,
                "website": contact_details.get("website"),
                "phone_nos": contact_details.get("phone_nos"),
                "fax": contact_details.get("fax"),
                "email_address": contact_details.get("email_address"),
                "main_campus_address": contact_details.get("main_address"),
                "latitude": inst_contact.get("lat"),
                "longitude": inst_contact.get("lng"),
                "logo": logo.get("logo"),
                "brochure": None,#needs sign in to get brochure from shiksha
                "no_of_programs": institute_details.get("number_of_programs"),
                "no_of_international_students": institute_details.get("Total International Students"),
                "international_student_%": institute_details.get("% International Students"),
                "on_campus_hostel_availability": institute_details.get("on_campus_hostel"),
                "hostel_fee": institute_details.get("hostel_fee"),
                "hostel_fee_currency": institute_details.get("hostel_fee_currency_id"),
                "qs_ranking": rank_uni.get("qs_ranking"),
                "qs_ranking_year" :rank_uni.get("qs_ranking_year"),
                "times_higher_education": rank_uni.get("times_higher_education"),
                "times_higher_education_year": rank_uni.get("times_higher_education_year"),
                "usnews": rank_uni.get("usnews"),
                "usnews_year": rank_uni.get("usnews_year"),
                "intake_month": intake_months.get("intake_month"),
                "intake_month_1": intake_months.get("intake_month_1"),
                "intake_month_2": intake_months.get("intake_month_2"),
            }
        }
    except KeyError:
        print('key: value not found')
    except ValueError as str_err:
        print('error while parsing string' + str_err.message)
    finally:
        pass
        # print(institute_dict)
        write_json(institute_dict, url.split('/')[-1])


if __name__ == "__main__":

    # universities = ["https://studyabroad.shiksha.com/usa/universities/stanford-university",
    #                 "https://studyabroad.shiksha.com/usa/universities/arizona-state-university",
    #                 "https://studyabroad.shiksha.com/usa/universities/the-university-of-texas-at-dallas",
    #                 "https://studyabroad.shiksha.com/usa/universities/massachusetts-institute-of-technology",
    #                 "https://studyabroad.shiksha.com/usa/universities/california-state-university-los-angeles-campus"]

    try:
        database = DBQueries()
        conx = database.connect("Institute")
        ids_urls = database.get_records(conx, "SELECT * FROM institute_urls where institute_id>1000 order by institute_id limit 5")
        conx.close()
        del database
        for id_url in ids_urls:
            institute_id = id_url[0]
            institute_url = id_url[1]
            print(str(institute_id)+"=>"+institute_url)
            scrape_institute(institute_url, institute_id)
    except ConnectionError:
        pass
    finally:
        pass
