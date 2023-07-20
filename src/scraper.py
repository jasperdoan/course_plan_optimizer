from urllib.request import urlopen

url = 'https://www.ics.uci.edu/ugrad/courses/listing-course.php?year=2023&level=ALL&department=INF&program=ALL'

page = urlopen(url)

html = page.read().decode("utf-8")

sindex = html.find('["id":protected]=>')
eindex = html.find('["description":protected]=>' , sindex)


dict = {}


while True:
    if sindex == -1 or eindex == -1:
        break

    aval_idx = html[sindex:html.find('["cores":protected]=>' , sindex)]
    SESSIONS = ['Fall', 'Winter', 'Spring']
    availability = []
    for session in SESSIONS:
        if session in aval_idx:
            availability.append(session)    
    
    info = html[sindex:eindex]
    
    course_idx = info.find('string(3) ')
    course_idx = info.find('string(3) ', course_idx + 1)
    course_title = info[course_idx + 11:course_idx + 14]

    cnum_idx = info.find('string(', course_idx + 1)
    course_num = info[cnum_idx + 10:cnum_idx + 16]
    course_num = course_num.replace('"', '')
    course_num = course_num.replace(' ', '')
    course_num = course_num.replace('\n', '')

    
    dict[course_title + ' ' + course_num] = availability


    sindex = html.find('["id":protected]=>', eindex)
    eindex = html.find('["description":protected]=>', sindex)


for key, value in dict.items():
    print(key, value)