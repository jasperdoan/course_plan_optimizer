import json
import os
import time
import re
import google.generativeai as genai
from dotenv import load_dotenv
import ast

def read_gemini_prompt():
    """Read the Gemini prompt template from file."""
    FILE_PATH = "gemini_prompt.txt"
    try:
        print(f"Reading prompt template from {FILE_PATH}...")
        with open(FILE_PATH, 'r', encoding='utf-8') as file:
            prompt = file.read()
        print(f"Successfully loaded prompt template ({len(prompt)} characters)")
        return prompt
    except FileNotFoundError:
        print(f"Error: {FILE_PATH} not found. Please create this file with the prompt template.")
        return ""

def initialize_gemini():
    """Initialize and configure the Gemini model."""
    print("Initializing Gemini model...")
    load_dotenv()  # Load environment variables from .env file
    api_key = os.getenv('GOOGLE_API_KEY')
    
    if not api_key:
        print("Warning: GOOGLE_API_KEY environment variable is not set. LLM validation will be skipped.")
        return None
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-lite')
    print("Gemini model initialized successfully")
    return model

# Track API calls for rate limiting
api_calls = {
    'count': 0,
    'last_reset_time': time.time(),
    'minute_count': 0
}

def parse_with_gemini(model, prompt_template, prereq_text):
    """
    Use Gemini to parse prerequisite text into logical structure.
    Implements rate limiting to prevent API rate limit errors.
    """
    if not prereq_text or prereq_text == "N/A":
        print("  No prerequisites to parse")
        return "N/A"
    
    if not model:
        print("  Skipping LLM parsing (no model available)")
        return "N/A"
    
    # Rate limiting logic - max 15 RPM (requests per minute)
    current_time = time.time()
    
    # Reset the counter if a minute has passed
    if current_time - api_calls['last_reset_time'] >= 60:
        print(f"Resetting API rate limit counter (was {api_calls['minute_count']})")
        api_calls['last_reset_time'] = current_time
        api_calls['minute_count'] = 0
    
    # Check if we're at the rate limit
    if api_calls['minute_count'] >= 14:  # Keep a buffer of 1 below the actual limit
        wait_time = 60 - (current_time - api_calls['last_reset_time'])
        if wait_time > 0:
            print(f"Rate limit reached. Waiting for {wait_time:.2f} seconds...")
            time.sleep(wait_time + 1)  # Add 1 second buffer
            # Reset after waiting
            api_calls['last_reset_time'] = time.time()
            api_calls['minute_count'] = 0
    
    # Prepare the prompt with the current prereq text
    prompt = f"{prompt_template}\n\nPrerequisite Text: {prereq_text}"
    
    try:
        print(f"  Sending API request for: {prereq_text[:100]}{'...' if len(prereq_text) > 100 else ''}")
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(temperature=0.0),
            stream=False
        )
        
        # Update API call tracking
        api_calls['count'] += 1
        api_calls['minute_count'] += 1
        
        print(f"  API call successful. Total calls: {api_calls['count']}, Minute count: {api_calls['minute_count']}")
        
        # Extract the result from the response
        result_text = response.text.strip()
        print(f"  LLM raw output: {result_text}")
        
        # If the response is just "N/A" (with or without quotes), return "N/A"
        if result_text in ['"N/A"', "'N/A'", "N/A"]:
            return "N/A"
        
        # Clean up any markdown code block formatting
        cleaned_text = re.sub(r'^```(?:json)?\s*', '', result_text)
        cleaned_text = re.sub(r'\s*```$', '', cleaned_text)
        
        # Handle the response based on content type
        try:
            # First try parsing as JSON
            final_result = json.loads(cleaned_text)
            print(f"  Successfully parsed as JSON")
            return final_result
        except json.JSONDecodeError as json_err:
            # Try to read it as a string and load it as a Python literal
            print(f"  JSON parsing error: {json_err}")
            final_result = f'{cleaned_text}'
            print(f"  Successfully parsed as Python literal")
            return final_result

            
    except Exception as e:
        print(f"  Error with LLM parsing: {e}")
        return "N/A"

def convert_prereqs_to_logical_structure(json_data, output_file):
    """
    Process each course in the JSON data to convert prerequisites to logical structure.
    """
    # Initialize Gemini model
    model = initialize_gemini()
    prompt_template = read_gemini_prompt()
    
    # Process each course
    processed_count = 0
    total_courses = len(json_data)
    print(f"Starting processing of {total_courses} courses...")
    
    start_time = time.time()
    
    for course_id, course_data in json_data.items():
        processed_count += 1
        print(f"\n[{processed_count}/{total_courses}] Processing course: {course_id}")
        
        prereq_text = course_data.get("prerequisites", "N/A")
        print(f"  Original prerequisites: {prereq_text}")
        
        # Parse prerequisites using Gemini
        parsed_prereqs = parse_with_gemini(model, prompt_template, prereq_text)
        print(f"  Parsed prerequisites: {parsed_prereqs}")
        
        # Update the course data with the structured prerequisites
        course_data["parsed_prerequisites"] = parsed_prereqs
        
        # Progress tracking and periodic saving
        if processed_count % 10 == 0:
            current_time = time.time()
            elapsed_time = current_time - start_time
            avg_time_per_course = elapsed_time / processed_count
            estimated_time_remaining = avg_time_per_course * (total_courses - processed_count)
            
            print(f"\n>>> Progress update: Processed {processed_count}/{total_courses} courses ({processed_count/total_courses*100:.1f}%)")
            print(f">>> Elapsed time: {elapsed_time:.1f}s, Est. time remaining: {estimated_time_remaining:.1f}s (~{estimated_time_remaining/60:.1f} min)")
            
            # Periodically save in case of interruption
            with open(f"{output_file}.partial", 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=4)
            print(f"Saved intermediate results to {output_file}.partial")
    
    # Save the final updated data to the output JSON file
    print(f"\nProcessing complete. Saving final results to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=4)
    
    print(f"Completed processing {processed_count} courses. Output saved to {output_file}")
    print(f"Total API calls made: {api_calls['count']}")

def main():
    """Main function to process course data."""
    print("=== Starting Course Prerequisite Processing ===")
    input_file = "course_data.json"
    output_file = "course_data_with_logical_prereqs.json"
    
    # Load the course data
    print(f"Loading course data from {input_file}...")
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        print(f"Successfully loaded {len(json_data)} courses from {input_file}")
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: {input_file} contains invalid JSON.")
        return
    
    # Process the data
    start_time = time.time()
    convert_prereqs_to_logical_structure(json_data, output_file)
    end_time = time.time()
    
    print(f"=== Processing Complete ===")
    print(f"Total execution time: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()
