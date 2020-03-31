"""
author : Jayapraveen
Date : 31/3/2020
Program Aim : To generate downloadable course data from the Guvi platform by making use of the covid19 offer
Version : v1.0
Method : Bruteforce, naive and tightly coupled to api endpoints
Status : Working
Preconditions : Enroll in all the courses before attempting to download the courses and complete the quiz in Python , Java and Cpp Courses
"""

import requests
import json
import os

#Global variables
data_type = ["onload","fetch-course","get-sublesson"] #various types of requests that can be sent
data_prefix = """--1
content-disposition: form-data; name="myData"
Content-Length: 246

"""
device = "mobile"
header = header = {"Host":"www.guvi.in","accept":"application/json, text/plain, */*","content-type":"multipart/form-data; boundary=1","accept-encoding":"gzip"}
data_suffix = """
--1--"""


def login():
    login_endpoint = "https://www.guvi.in/model/v2/mobileEndpoint/usercheck.php"
    header = {"Host": "www.guvi.in","content-type": "multipart/form-data; boundary=1","accept-encoding": "gzip"}
    data = """--1
content-disposition: form-data; name="myData"
Content-Length: 88

{"emails":"","","authtoken":null,"device":"mobile"}
--1--"""
    data = requests.post(url = login_endpoint,data = data,headers = header)
    data = json.loads(data.text)
    #print(data['auth'])
    return data['auth'] # return authentication token

def course_fetcher(token): # To find the paid course details
    endpoint = "https://www.guvi.in/model/v2/courseFetch.php"

    final_data = "{" + f"\"requestType\":\"{data_type[0]}\",\"authtoken\":\"{token}\",\"device\":\"{device}\"" + "}"
    final_data = data_prefix + final_data + data_suffix
    out_data = requests.post(url = endpoint, data = final_data, headers = header)
    out_data = json.loads(out_data.text)
    paid = json.loads(out_data['allCourses']) # need to load the data as json several times as the api returning data is crappy and sh!t
    enrolled_courses = json.loads(out_data['myCourses'])
    paid_programs = [] # to append the course identifier data
    for i in enrolled_courses:
        paid_programs.append(i['ckey'])
    return paid_programs

def get_course_url(lesson_details,course_id):
    endpoint = "https://www.guvi.in/model/v2/course_content.php"
    for i in lesson_details:
        final_data = "{" + f"\"type\":\"{data_type[2]}\",\"courseId\":\"{course_id}\",\"sublessonId\":\"{i}\",\"authtoken\":\"{token}\",\"device\":\"{device}\"" + "}"
        final_data = data_prefix + final_data + data_suffix
        print(final_data)
        out_data = requests.post(url = endpoint, data = final_data, headers = header)
        sublesson = out_data.text
        final_data = open(i+".txt",'w')
        final_data.write(sublesson)

def course_info(paid_program_details):
    endpoint = "https://www.guvi.in/model/v2/course_content.php"
    for course in paid_program_details:
        final_data = "{" + f"\"type\":\"{data_type[1]}\",\"courseId\":\"{course}\",\"authtoken\":\"{token}\",\"device\":\"{device}\"" + "}"
        final_data = data_prefix + final_data + data_suffix
        out_data = requests.post(url = endpoint, data = final_data, headers = header)
        out_data = out_data.text
        data = json.loads(out_data)
        if not os.path.exists(course):
            os.makedirs(course)
        os.chdir(course)
        lesson_details = []
        for i in data:
            lesson_details.append(i['lessonId'])
        get_course_url(lesson_details, course)
        course_data = open("course.txt",'w')
        course_data.write(out_data)
        os.chdir('../')

if __name__ == '__main__':
    token = login()
    paid_program_details = course_fetcher(token)
    course_info(paid_program_details)