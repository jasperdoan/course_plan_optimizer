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