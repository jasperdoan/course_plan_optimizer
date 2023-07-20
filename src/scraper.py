from urllib.request import urlopen
from dataclasses import dataclass

@dataclass
class AvailabilityScraper:
    year: int
    level: str
    department: str
    program: str

    @property
    def course_availability(self) -> dict:
        return self._course_availability
    
    def __post_init__(self):
        self._url = f'https://www.ics.uci.edu/ugrad/courses/listing-course.php?year={self.year}&level={self.level}&department={self.department}&program={self.program}'
        
        self._html = urlopen(self._url).read().decode('utf-8')
        self._sindex = self._html.find('["id":protected]=>')
        self._eindex = self._html.find('["description":protected]=>', self._sindex)
        self._course_availability = {}
        self.__scrape()

    def __scrape(self) -> None:
        while True:
            if self._sindex == -1 or self._eindex == -1:
                break

            aval_idx = self._html[self._sindex:self._html.find('["cores":protected]=>', self._sindex)]
            SESSIONS = ['Fall', 'Winter', 'Spring']
            availability = []
            for session in SESSIONS:
                if session in aval_idx:
                    availability.append(session)

            info = self._html[self._sindex:self._eindex]

            course_idx = info.find('string(3) ')
            course_idx = info.find('string(3) ', course_idx + 1)
            course_title = info[course_idx + 11:course_idx + 14]

            cnum_idx = info.find('string(', course_idx + 1)
            course_num = info[cnum_idx + 10:cnum_idx + 16]
            course_num = course_num.replace('"', '')
            course_num = course_num.replace(' ', '')
            course_num = course_num.replace('\n', '')

            self._course_availability[course_title + ' ' + course_num] = availability

            self._sindex = self._html.find('["id":protected]=>', self._eindex)
            self._eindex = self._html.find('["description":protected]=>', self._sindex)
