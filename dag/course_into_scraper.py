import requests
from bs4 import BeautifulSoup
import json
import re

def clean_text(text):
    """Replace non-breaking spaces with regular spaces."""
    if isinstance(text, str):
        # Remove \u00a0 (non-breaking space), leading/trailing whitespace, and any characters that comes after '.\n' and '.\n' themselves
        return re.sub(r'\s+', ' ', text.replace('\u00a0', ' ').strip()).replace('.\n', '').replace('\n', '')
    return text

def scrape_course_catalog(url):
    """Scrape course information from a UCI catalog page."""
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve data from {url}")
        return {}
    
    soup = BeautifulSoup(response.text, 'html.parser')
    course_blocks = soup.find_all('div', class_='courseblock')
    
    courses = {}
    
    for course_block in course_blocks:
        # Extract course title block
        title_block = course_block.find('p', class_='courseblocktitle')
        if not title_block or not title_block.strong:
            continue
            
        # Parse title text which is in format: "SUBJECT NUM. Title. Units."
        title_text = clean_text(title_block.strong.text)
        
        # Debug
        # print(f"Processing: {title_text}")
        
        # More flexible regex that handles all variations
        match = re.match(r'([A-Z0-9&_\s]+)\s+([H]?\d+[A-Z]?(?:LA|LB|L|W|S)?)\.\s+(.*?)\.\s+(\d+(?:-\d+)?(?:\.\d+)?)\s+((?:Workload )?Units?)\.\s*', title_text)

        if not match:
            print(f"Failed to match: {title_text}")
            continue
            
        subject, number, title, units, unit_type = match.groups()
        subject = clean_text(subject)
        number = clean_text(number)
        title = clean_text(title)
        units = clean_text(units)
        course_id = f"{subject} {number}"
        
        # Store unit_type if needed (whether it's "Units", "Unit" or "Workload Units")
        # You can uncomment this if you want to store the unit type in your JSON
        # unit_type = clean_text(unit_type)
        
        # Extract description block
        desc_block = course_block.find('div', class_='courseblockdesc')
        if not desc_block:
            continue
            
        # Get all paragraph elements
        paragraphs = desc_block.find_all('p')
        
        # First paragraph is always the description
        description = clean_text(paragraphs[0].text) if paragraphs else "N/A"
        
        # Initialize optional fields
        prerequisites = "N/A"
        overlaps_with = "N/A"
        same_as = "N/A"
        restriction = "N/A"
        grading_option = "N/A"
        
        # Process remaining paragraphs for other information
        for p in paragraphs[1:] if len(paragraphs) > 1 else []:
            text = clean_text(p.text)
            
            if text.startswith("Prerequisite"):
                prerequisites = clean_text(text[13:])
            elif text.startswith("Same as"):
                same_as = clean_text(text[8:])
            elif text.startswith("Restriction"):
                restriction = clean_text(text[11:])
            elif text.startswith("Grading Option"):
                grading_option = clean_text(text[15:])
            if "Overlaps with" in text:
                overlaps_with = clean_text(text.split("Overlaps with")[1].strip())
        
        # Store course information
        courses[course_id] = {
            "title": title,
            "units": units,
            "description": description,
            "prerequisites": prerequisites,
            "overlaps_with": overlaps_with,
            "same_as": same_as,
            "restriction": restriction,
            "grading_option": grading_option
        }
    
    return courses

def main():
    urls = [
        "https://catalogue.uci.edu/allcourses/compsci/",
        "https://catalogue.uci.edu/allcourses/i_c_sci/",
        "https://catalogue.uci.edu/allcourses/in4matx/",
        "https://catalogue.uci.edu/allcourses/stats/",
        "https://catalogue.uci.edu/allcourses/math/",
    ]
    
    all_courses = {}
    
    for url in urls:
        print(f"Scraping {url}")
        courses = scrape_course_catalog(url)
        all_courses.update(courses)
        print(f"Found {len(courses)} courses")
    
    # Save to JSON file
    output_path = "course_data.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_courses, f, indent=4)
    
    print(f"Saved {len(all_courses)} courses to {output_path}")

if __name__ == "__main__":
    main()
