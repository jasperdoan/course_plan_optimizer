import pandas as pd
from urllib.request import urlopen
from typing import NamedTuple


class UCIScaperIdentifier(NamedTuple):
    url_link: str = f'https://www.ics.uci.edu/ugrad/courses/listing-course.php'
    decoder: str = 'utf-8'
    stable: str = '["id":protected]=>'
    estable: str = '["description":protected]=>'
    avail: str = '["cores":protected]=>'
    sessions: list = ['Fall', 'Winter', 'Spring']
    course_idx: str = 'string('


def scrape_avail_listings(year: int, department: str, level: str = 'ALL', program: str = 'ALL') -> dict:
    uid = UCIScaperIdentifier()
    url = f'{uid.url_link}?year={year}&level={level}&department={department}&program={program}'
    html = urlopen(url).read().decode(uid.decoder)
    sidx = html.find(uid.stable)
    eidx = html.find(uid.estable, sidx)

    def strip(string: str) -> str:
        return string.replace('"', '').replace(' ', '').replace('\n', '')

    course_availability = {}

    while True:
        if sidx == -1 or eidx == -1:
            break

        aval_idx = html[sidx:html.find(uid.avail, sidx)]
        availability = [s for s in uid.sessions if s in aval_idx]

        info = html[sidx:eidx]

        cidx = info.find(uid.course_idx)    # Skip first instance

        cidx = info.find(uid.course_idx, cidx + 1)
        ctitle = info[cidx + 11:cidx + 11 + len(department)]
        ctitle = strip(ctitle)

        nidx = info.find(uid.course_idx, cidx + 1)
        cnum = info[nidx + 10:nidx + 16]
        cnum = strip(cnum)

        course_availability[ctitle + ' ' + cnum] = availability

        sidx = html.find(uid.stable, eidx)
        eidx = html.find(uid.estable, sidx)

    return course_availability


def save_csv(file_path: str, data: dict) -> None:
    for k, v in data.items():
        data[k] = '+'.join(v)

    df = pd.DataFrame(data.items(), columns=['Course', 'Availability'])
    df.to_csv(file_path, index=False)


def read_csv(file_path: str) -> dict:
    df = pd.read_csv(file_path)
    course_dict = {}

    for _, row in df.iterrows():
        course_id = row['Course']
        availability = row['Availability']
        course_dict[course_id] = [] if pd.isnull(availability) else availability.split('+')

    return course_dict



# avail_dict = {
#     **scrape_avail_listings(year=2023, department='CS'), 
#     **scrape_avail_listings(year=2023, department='INF'),
#     **scrape_avail_listings(year=2023, department='ICS'),
#     **scrape_avail_listings(year=2023, department='STATS')
# }

# csv_file_path = 'data\course_avail.csv'


# # Change avail_dict.values() from list to string
# for k, v in avail_dict.items():
#     avail_dict[k] = '+'.join(v)


# df = pd.DataFrame(avail_dict.items(), columns=['Course', 'Availability'])
# df.to_csv(csv_file_path, index=False)
