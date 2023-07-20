from urllib.request import urlopen

url = 'https://www.ics.uci.edu/ugrad/courses/listing-course.php?year=2023&level=ALL&department=INF&program=ALL'

page = urlopen(url)

html = page.read().decode("utf-8")

sindex = html.find('["id":protected]=>')
eindex = html.find('["description":protected]=>' , sindex)

while True:
    if sindex == -1 or eindex == -1:
        break
    
    info = html[sindex:eindex]
    # print(info)

    course_idx = info.find('string(3) ')
    course_idx = info.find('string(3) ', course_idx + 1)
    course_title = info[course_idx + 11:course_idx + 14]

    cnum_idx = info.find('string(', course_idx + 1)
    course_num = info[cnum_idx + 10:cnum_idx + 16]
    course_num = course_num.replace('"', '')
    course_num = course_num.replace(' ', '')
    course_num = course_num.replace('\n', '')

    desc_idx = info.find('string(', cnum_idx + 1)
    course_desc = info[desc_idx + 12:len(info) - 4]

    print(f'{course_title} {course_num} {course_desc}')


    print('--------------------------')

    sindex = html.find('["id":protected]=>', eindex)
    eindex = html.find('["description":protected]=>', sindex)

