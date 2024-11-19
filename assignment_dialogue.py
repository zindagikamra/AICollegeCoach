import os
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime, time, timedelta
import json

# Load environment variables
load_dotenv()

MODEL_NAME = os.getenv("OPENAI_MODEL_NAME")

# Initialize OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    organization=os.getenv("OPENAI_ORGANIZATION_ID")
)  # It will automatically use OPENAI_API_KEY from environment

# Debug prints
print(f"API Key (first 5 chars): {os.getenv('OPENAI_API_KEY')[:5]}...")
print(f"Organization ID: {os.getenv('OPENAI_ORGANIZATION_ID')}")
print(f"Model Name: {MODEL_NAME}")

# Add after client initialization
try:
    print(f"\nCurrent Organization Settings:")
    print(f"Organization ID: {os.getenv('OPENAI_ORGANIZATION_ID')}")
    
    # List available models
    available_models = client.models.list()
    print("\nAvailable Models:")
    for model in available_models:
        print(model.id)
        
    # Try to get organization info
    org_info = client.organizations.get()  # Note: This might not work in current API version
    print(f"\nOrganization Name: {org_info.name if org_info else 'Unable to fetch'}")
except Exception as e:
    print(f"Error: {e}")

assignments = []

def get_initial_assignment_info():
    prompt = """
    Tell me about an upcoming exam or assignment you have! 
    Please include:
    - When it's due (date and time)
    - How much time you think you'll need (in hours)
    - How many study sessions you'd like to break it into
    For example: "My AI Programming Assignment #3 is due next Saturday at 6pm. I think it'll take 8 hours. Break that down into 4 sessions."
    """
    
    print("\nAI College Coach: " + prompt)
    user_response = input("You: ")
    return user_response

def process_assignment_dialogue(user_input, assignment_data):
    current_date = datetime.now()
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": f"""
                Extract assignment information and respond in JSON format.
                Today is {current_date.strftime('%Y-%m-%d')}.
                When processing relative dates (like 'next Saturday' or 'tomorrow'):
                - Today is {current_date.strftime('%A, %B %d, %Y')}
                - Calculate exact dates from this reference point
                - Do not reuse dates from past years. It is currently {current_date.strftime('%Y')}.
                
                Use null if information is missing.
                Keys:
                - name (generate a descriptive name)
                - due date (YYYY-MM-DD)
                - due time (HH:MM 24-hour format)
                - time_allocated (minutes)
                - sessions (number)
                Example: {{
                    "name": "AI Programming Assignment 3",
                    "due date": "2024-11-23",
                    "due time": "18:00",
                    "time_allocated": 480,
                    "sessions": 4
                }}
            """},
            {"role": "user", "content": user_input}
        ]
    )
    
    # Parse JSON response
    extracted_info = json.loads(response.choices[0].message.content)
    
    # Convert date and time strings to datetime objects
    if extracted_info.get('due date'):
        extracted_info['due date'] = datetime.strptime(extracted_info['due date'], '%Y-%m-%d').date()
    if extracted_info.get('due time'):
        extracted_info['due time'] = datetime.strptime(extracted_info['due time'], '%H:%M').time()
    
    # Update assignment_data
    assignment_data.update(extracted_info)
    
    # Return missing fields
    missing_fields = [k for k, v in assignment_data.items() if v is None]
    return missing_fields

def handle_missing_info(missing_fields, assignment_data):
    current_date = datetime.now()
    # Generate comprehensive follow-up question using GPT
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": """
                Generate a natural follow-up question asking for all of the missing information.
                For example, if the missing fields are "due date" and "due time", the question should be something
                like "Can you tell me the date and time it's due (or when the exam is)?"
            """},
            {"role": "user", "content": f"Generate a question asking for these missing inputs: {', '.join(missing_fields)}"}
        ]
    )
    
    # Get the follow-up question
    question = response.choices[0].message.content
    print("\nAI College Coach:", question)
    
    # Get user's response
    user_response = input("You: ")
    
    # Process the response for all fields
    field_response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": f"""
                Extract the following fields from the response and format in JSON:
                {', '.join(missing_fields)}

                Today is {current_date.strftime('%Y-%m-%d')}.
                When processing relative dates (like 'next Saturday' or 'tomorrow'):
                - Use current date as reference
                
                Use the same format as the main dialogue:
                - due date: YYYY-MM-DD
                - due time: HH:MM in 24-hour format
                - time_allocated: minutes (convert from hours if needed)
                - sessions: number
                
                Return only these fields in JSON format.
            """},
            {"role": "user", "content": user_response}
        ]
    )
    
    # Update the specific fields
    extracted_info = json.loads(field_response.choices[0].message.content)
    
    # Convert date/time if needed
    if 'due date' in extracted_info:
        extracted_info['due date'] = datetime.strptime(extracted_info['due date'], '%Y-%m-%d').date()
    if 'due time' in extracted_info:
        extracted_info['due time'] = datetime.strptime(extracted_info['due time'], '%H:%M').time()
    
    # Update assignment_data with new values
    assignment_data.update(extracted_info)

def collect_assignment_info():
    assignment_data = {
        "name": None,
        "due date": None,
        "due time": None,
        "time_allocated": None,
        "sessions": None
    }
    
    # Get and process initial response
    user_input = get_initial_assignment_info()
    missing_fields = process_assignment_dialogue(user_input, assignment_data)
    
    # Handle follow-ups if needed
    if missing_fields:
        handle_missing_info(missing_fields, assignment_data)
    
    # Add to assignments list
    assignments.append(assignment_data)
    
    # Ask about another assignment
    another = input("\nWould you like to add another exam or assignment? (yes/no): ").lower()
    if another in ['y', 'yes']:
        collect_assignment_info()  # Recursive call
    
    return assignments

if __name__ == "__main__":
    collect_assignment_info()
    print(assignments)