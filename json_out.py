import json

import requests
from bs4 import BeautifulSoup
import re
import inspect


from database import DBQueries


def write_json(details_dict, f_name=""):
    json_object = json.dumps(details_dict, indent=2)
    filename = "out_files/json/" + f_name + ".json"
    with open(filename, "w") as outfile:
        outfile.write(json_object)

def lineno():
    """Returns the current line number in our program."""
    return inspect.currentframe().f_back.f_lineno

def dict_clean(dict):
    result = {}
    for key, value in dict.items():
        if value is None:
            value = ''
        result[key] = value
    return result


def scrape_institute(url, id):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    institute = {}
    try:
        title = soup.find('h1', attrs={"class": "H1-sc-1225uyb-0 KmIux"}).text
        _, institute_type, established_year_ = soup.find('div', attrs={
            "class": "Styled__UnivLinks-sc-132amsi-4 gXZkCE"}).text.split('|')
        # print(institute_type)
        established_year = ''.join(filter(str.isdigit, established_year_))
        # print(established_year)
        institute.update({
            "name": title.split('(')[0],
            "established_year": established_year,
            "institute_type": institute_type,
        })
        places = soup.find('span', attrs={"class": "loc-icn"}).text.split(',')
        if(len(places) == 2):
            # print('state does not exist', places)
            institute.update({
                "city": places[0].strip(),
                "country": places[1].strip(),
            })
        elif(len(places) == 3):
            # print('state exist', places)
            institute.update({
                "city": places[0].strip(),
                "state": places[1].strip(),
                "country": places[2].strip(),
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
        hostel = institute_details.get("Yearly Hostel & Meals Expense")
        if hostel is None:
            institute_details.update({
                "on_campus_hostel": "No",
            })
        else:
            hfee = hostel.split(' ')[1]
            hfee = float(hfee)*100000
            institute_details.update({
                "on_campus_hostel": "Yes",
                "hostel_fee": hfee,
                "hostel_fee_currency_id": hostel.split(' ')[0],
            })
        # print(hostel.p.text)
    except IndexError:
        pass
    except AttributeError:
        pass
    except ValueError as ve:
        print('error converting fee denomination', ve)

    # print(institute_details)

    apfee = {}
    try:
        app_fee = soup.find('td', string="Application fees")
        application_fees = app_fee.find_next_sibling('td').text.split(' ')
        apfee.update({"application_fee_currency": application_fees[0],
                    "application_fee": application_fees[1:]})
    except IndexError:
        pass
    except AttributeError:
        pass

    rank_uni = {}
    try:
        rankings__ = soup.find_all('div', attrs={"class": "Styled__RankingListBox-sc-132amsi-9 iVoSAn"})
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
        if (intake_month[0].text == "Intake Season & Deadlines"):
            intakes = intake_month[1].find_all('div')
            intake_index = 0
            im = "intake_month"
            for intake in intakes:
                # print(intake.text)
                intake_months.update({im: intake.text.split(' ')[-2]})
                intake_index += 1
                im = "intake_month_" + str(intake_index)
            intake_months.update({
                "season": intakes[0].text.split(':')[0],
                "date": intakes[0].text.split(':')[1]
            })
    except IndexError:
        pass
    except AttributeError:
        pass


    inst_contact = {}
    try:
        lat_lng_a = soup.find('div', attrs={"class": "Styled__ContactUsMapDiv-sc-1yl1nt-11 byPnsn"})
        lat_lng_url = lat_lng_a.find('a', href=True)['href']
        # lat_lng = lat_lng_url.split('/')[-1].split(',')
        inst_contact.update({"lat": lat_lng_url.split('/')[-1].split(',')[0]})
        inst_contact.update({"lng": lat_lng_url.split('/')[-1].split(',')[1]})
    except AttributeError as aerr:
        pass
        # print(aerr)
        # print(lineno())
    except IndexError as err:
        pass
    # print(lat_lng)

    logo = {}
    try:
        logo_link_ = soup.find('img', attrs={"class": "Styled__ImageDiv-sc-5p2r35-0 gYjxkS"})
        # print(logo_link_)
        logo_link = logo_link_['src']
        logo.update({"logo": logo_link})
    except (AttributeError, IndexError, TypeError) as e:
        pass

    try:
        institute_dict = {
            institute.get("name"): {
                "name_of_the_university": institute.get("name"),
                "short_name": None,  # do we need to make it or get from the name of the insti
                "establishment_year": institute.get("established_year"),
                "institute_type": institute.get("institute_type"),
                "country": institute.get("country"),
                # need to use API to get next three fields as per the excel sheet, else this info can be extracted from the page itself
                "state": institute.get("state"),
                "city": institute.get("city"),
                "website": contact_details.get("website"),
                "phone_no": contact_details.get("phone_nos"),
                "fax": contact_details.get("fax"),
                "email_address": contact_details.get("email_address"),
                "main_campus_address": contact_details.get("main_address"),
                "latitude": inst_contact.get("lat"),
                "longitude": inst_contact.get("lng"),
                "logo": logo.get("logo"),
                "brochure": None,  # needs sign in to get brochure from shiksha
                "no_of_programs": institute_details.get("number_of_programs"),
                "no_of_international_students": institute_details.get("Total International Students"),
                "international_student_%": institute_details.get("% International Students"),
                "on_campus_hostel_availability": institute_details.get("on_campus_hostel"),
                "hostel_fee": institute_details.get("hostel_fee"),
                "hostel_fee_currency": institute_details.get("hostel_fee_currency_id"),
                "qs_ranking": rank_uni.get("qs_ranking"),
                "qs_ranking_year": rank_uni.get("qs_ranking_year"),
                "times_higher_education": rank_uni.get("times_higher_education"),
                "times_higher_education_year": rank_uni.get("times_higher_education_year"),
                "usnews": rank_uni.get("usnews"),
                "usnews_year": rank_uni.get("usnews_year"),
                "intake_month": intake_months.get("intake_month"),
                "intake_month_1": intake_months.get("intake_month_1"),
                "intake_month_2": intake_months.get("intake_month_2"),
            },
        }
        details_for_course = {
            'application_fee': apfee.get("application_fee"),
            'application_fee_currency': apfee.get("application_fee_currency"),
            'date_type': 'Application End Date',#where are these field??
            'season': 'June',
            'date': '30, 2020',
        }
    except KeyError:
        print('key: value not found')
    except ValueError as str_err:
        print('error while parsing string' + str_err.message)
    finally:
        pass
        # print(institute_dict)
        institute_dict = dict_clean(institute_dict.get(institute.get("name")))
        # print(institute_dict)
        # write_json(institute_dict, url.split('/')[-1])
        return institute.get("name"), details_for_course, institute_dict


def scrape_rurl_courses(url):
    rurls = []
    response = requests.get(url + "/courses")
    soup = BeautifulSoup(response.content, "html.parser")
    links__ = soup.find_all('a', attrs={"class": "Styled__LinkStyle-sc-19aj422-2 jRTEUB"})
    for l in links__:
        link = l['href']
        if link not in rurls:
            rurls.append(link)
            # print(link)
    return rurls


def scrape_course_details(rurl, details_for_course):
    url = "https://studyabroad.shiksha.com" + rurl
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
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
    except (IndexError, TypeError, AttributeError):
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
    except (IndexError, TypeError, AttributeError):
        pass
    # print(coursedetails)

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
    except (IndexError, TypeError, AttributeError):
        pass
    # print(exams_entrance)

    exams = []
    exams_score = []
    for exam, exam_score in exams_entrance.items():
        exams.append(exam.split(' ')[0])
        exams_score.append(exam_score)
    try:
        course_dtls = {
            'level': coursedetails.get("level_id"),
            'stream': '??',# TODO: from where did you pick up the following
            'degree': '??',
            'specialization': '??',
            'course_name': coursedetails.get("name"),
            'department/school': '??', #TODO: not there oon course details page
            'mode': '??', # TODO: not there in course details page
            'duration': coursedetails.get("course_duration"),
            'duration_type': coursedetails.get("duration_type"),
            'tuition_fees': coursedetails.get("fee"),#Styled__TableStyle-sc-10ucg51-0 vXiFr
            'tuition_fee_currency': coursedetails.get("fee"),
            'tuition_fee_duration_type': 'Annual ',#many don't have this
            'application_fee': details_for_course.get("application_fee"), #TODoThese fields are there in overview section receive it as an arg
            'application_fee_currency': details_for_course.get("application_fee_currency"),
            'exam': exams,
            'exam_section': [
                '??',
                '??'
            ],# TODO: what's this exam section in course details section??
            'exam_score': exams_score,
            'date_type': 'Application End Date',#TO ddDo the following are in overview page receive it as an arg
            'season': coursedetails.get("season"),
            'date': coursedetails.get("date"),
        }
    except (IndexError, TypeError, AttributeError):
        pass
    finally:
        pass
        # course_dtls = dict_clean(course_dtls)# TODO uncomment this line when all values of course details are finalized.
        return course_dtls

if __name__ == "__main__":

    # universities = ["https://studyabroad.shiksha.com/usa/universities/stanford-university",
    #                 "https://studyabroad.shiksha.com/usa/universities/arizona-state-university",
    #                 "https://studyabroad.shiksha.com/usa/universities/the-university-of-texas-at-dallas",
    #                 "https://studyabroad.shiksha.com/usa/universities/massachusetts-institute-of-technology",
    #                 "https://studyabroad.shiksha.com/usa/universities/california-state-university-los-angeles-campus"]

    create_queries = [
        f"CREATE TABLE universities ",
        f"CREATE TABLE courses"
    ]
    try:
        database = DBQueries()
        conx = database.connect("Institute")
        ids_urls = database.get_records(conx, "SELECT * FROM institute_urls where institute_id>1500 order by institute_id limit 2")
        conx.close()
        del database
        insts_dict = {}
        for id_url in ids_urls:
            institute_id = id_url[0]
            institute_url = id_url[1]
            print(str(institute_id) + "=>" + institute_url)
            name, details_for_course, inst_dict = scrape_institute(institute_url, institute_id)
            insts_dict.update({name: inst_dict})
            rurl_courses = scrape_rurl_courses(institute_url)
            # print(rurl_courses)
            courses_details = {
                "name_of_the_university": name,
                "courses": []
            }
            for rurl_course in rurl_courses:
                # print(rurl_course)
                course_dtls = scrape_course_details(rurl_course, details_for_course)
                # print(course_dtls)
                courses_details["courses"].append(course_dtls)
            write_json(courses_details, institute_url.split('/')[-1] + "_courses")
        # print(insts_dict)
    except (ConnectionError, ValueError):
        pass
    finally:
        write_json(insts_dict, "institutes")
        pass
