import json
import os
import google.generativeai as genai
import time
import re

# Read from text file for prompt 
FILE_PATH = "gemini_prompt.txt"
with open(FILE_PATH, 'r', encoding='utf-8') as file:
    PROMPT_TEMPLATE = file.read()


def setup_genai_api():
    """Set up the Gemini API with the API key."""
    api_key = ''
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is not set")
    
    genai.configure(api_key=api_key)
    # Use Gemini 2.0 Flash model instead of Pro
    return genai.GenerativeModel('gemini-2.0-flash')

def parse_prerequisites_with_gemini(text, model):
    """Parse prerequisites using Gemini API with rate limiting."""
    if not text or text.strip() == "N/A":
        return None
    
    prompt = PROMPT_TEMPLATE
    
    try:
        response = model.generate_content(
            f"{prompt}\n\n{str(text)}", 
            generation_config=genai.types.GenerationConfig(
                temperature=0.0
            ),
            stream=False
        )
        
        # Extract JSON from the response
        result = response.text
        

        if result:
            # Clean up any markdown code block formatting if present
            result = re.sub(r'^```json\s*', '', result)
            result = re.sub(r'\s*```$', '', result)

            print(result)

            return json.loads(result)
        return None
    except Exception as e:
        print(f"Error parsing prerequisites: {e}")
        return {"error": str(e), "text": text}

def process_course_data(json_path, model):
    """Process the course data and update with structured prerequisites."""
    with open(json_path, 'r', encoding='utf-8') as file:
        course_data = json.load(file)

    total_courses = len(course_data)
    processed = 0
    
    updated_course_data = {}
    
    # Track API calls per minute to respect rate limits
    minute_start = time.time()
    calls_in_current_minute = 0
    
    for course_id, course_info in course_data.items():
        # Rate limiting: Check if we're approaching limits
        current_time = time.time()
        if current_time - minute_start > 60:
            # Reset the counter for a new minute
            minute_start = current_time
            calls_in_current_minute = 0
        
        # If we're near the rate limit, pause
        if calls_in_current_minute >= 12:  # 12 instead of 15 to be safe
            sleep_time = 60 - (current_time - minute_start) + 1
            if sleep_time > 0:
                print(f"Approaching rate limit, pausing for {sleep_time:.1f}s...")
                time.sleep(sleep_time)
                minute_start = time.time()
                calls_in_current_minute = 0
        
        prereq_text = course_info.get('prerequisites', 'N/A')
        
        # Parse the prerequisites using Gemini
        print(f"Parsing prerequisites for {course_id}...")
        print(f"\n\n{prereq_text}")
        structured_prereqs = parse_prerequisites_with_gemini(prereq_text, model)
        calls_in_current_minute += 1
        
        # Add the updated course info to our new dictionary
        updated_course_data[course_id] = {
            "title": course_info.get('title', 'N/A'),
            "units": course_info.get('units', 'N/A'),
            "description": course_info.get('description', 'N/A'),
            "prerequisites": structured_prereqs,
            "overlaps_with": course_info.get('overlaps_with', 'N/A'),
            "same_as": course_info.get('same_as', 'N/A'),
            "restriction": course_info.get('restriction', 'N/A'),
            "grading_option": course_info.get('grading_option', 'N/A')
        }
        
        processed += 1
        if processed % 5 == 0:
            print(f"Processed {processed}/{total_courses} courses")
            # Additional sleep to ensure we're well under the rate limit
            time.sleep(0.5)
        
        # Every 100 requests, take a longer break to stay under token per minute limits
        if processed % 100 == 0 and processed > 0:
            print(f"Taking a break to respect TPM limits...")
            time.sleep(5)
    
    return updated_course_data

def save_course_data(course_data, output_path):
    """Save the updated course data to a JSON file."""
    with open(output_path, 'w', encoding='utf-8') as file:
        json.dump(course_data, file, indent=4)

def main():
    """Main function to parse prerequisites with Gemini."""
    try:
        # Set up the Gemini API
        model = setup_genai_api()
        
        # Path to the course data JSON file
        input_path = 'course_data.json'
        output_path = 'course_data_structured.json'
        
        # Process the course data
        print(f"Processing course data from {input_path}")
        updated_course_data = process_course_data(input_path, model)
        
        # Save the updated course data
        save_course_data(updated_course_data, output_path)
        print(f"Updated course data saved to {output_path}")
    
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
