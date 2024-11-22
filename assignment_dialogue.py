import os
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime, time
import json
import time
from scheduler_logic import slow_print
# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(
    # api_key=os.getenv("OPENAI_API_KEY"),
    # organization=os.getenv("OPENAI_ORGANIZATION_ID")
)  # It will automatically use OPENAI_API_KEY from environment

def get_initial_assignment_info(is_first_assignment=True):
    """
    Prompts the user for initial assignment information and returns their response.
    
    Args:
        is_first_assignment (bool): Whether this is the first assignment being entered
    
    Returns:
        str: The user's response containing assignment details
    """
    if is_first_assignment:
        prompt = """
    Tell me about an upcoming exam or assignment you have! 
    Please include:
    - When it's due (date and time)
    - How much time you think you'll need (in hours)
    - How many study sessions you'd like to break it into
    For example: "My AI Programming Assignment #3 is due next Saturday at 6pm. I think it'll take 8 hours. Break that down into 4 sessions."
    """
    else:
        prompt = """
    Tell me about another upcoming exam or assignment! Remember to include:
    - When it's due (date and time)
    - How much time you think you'll need (in hours)
    - How many study sessions you'd like to break it into
    """
    
    print("\nAI College Coach: ", end='')
    slow_print(prompt)
    slow_print("You: ")
    user_response = input()
    return user_response

def process_assignment_dialogue(user_input, assignment_data):
    """
    Processes user input to extract assignment information using GPT model.
    
    Args:
        user_input (str): Raw user input containing assignment details
        assignment_data (dict): Dictionary to store extracted assignment information
        
    Returns:
        list: List of missing fields that still need to be collected in the assignment (key values in the dictionary)
    """
    current_date = datetime.now()
    # Create the messages array
    messages = [
        {"role": "system", "content": f"""
                Extract assignment information and respond in JSON format.
                Today is {current_date.strftime('%Y-%m-%d')}.
                
                Return JSON with these fields:
                - name: descriptive name for the assignment
                - due date: YYYY-MM-DD
                - due time: HH:MM in 24-hour format
                - time_allocated: minutes (convert from hours)
                - sessions: number
                Make sure to return JUST the JSON, nothing else.
                Example Response:
                {{
                    "name": "Calculus Exam",
                    "due date": "2024-03-19",
                    "due time": "14:00",
                    "time_allocated": 180,
                    "sessions": 4
                }}
            """},
            {"role": "user", "content": user_input}
        ]
        
    response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
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
    """
    Handles collection of missing assignment information through follow-up questions.
    
    Args:
        missing_fields (list): List of fields that need to be collected
        assignment_data (dict): Dictionary to update with collected information
    """
    current_date = datetime.now()
    # Generate comprehensive follow-up question using GPT
    response = client.chat.completions.create(
        model='gpt-4o-mini',
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
    print("\nAI College Coach: ", end='')
    slow_print(question)
    
    # Get user's response
    slow_print("You: ")
    user_response = input()
    
    # Process the response for all fields
    field_response = client.chat.completions.create(
        model='gpt-4o-mini',
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

def handle_emotional_checkin():
    """
    Handles emotional check-in with the user regarding their assignments.
    Uses a fine-tuned model to detect emotions and provides supportive responses.
    """
    # Ask user about their feelings
    print("\nAI College Coach: ", end='')
    slow_print("How are you feeling about these assignments?")
    slow_print("You: ")
    user_response = input()
    
    # Get emotion from fine-tuned model
    emotion_response = client.chat.completions.create(
        model=os.getenv("OPENAI_FINETUNED_MODEL"),
        messages=[
            {"role": "system", "content": "Detect the emotions in the input in a couple words."},
            {"role": "user", "content": user_response}
        ]
    )
    detected_emotion = emotion_response.choices[0].message.content.strip()
    
    # Get supportive response from main model with streaming
    print("\nAI College Coach: ", end='', flush=True)  # Print prefix without newline
    stream = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[
            {"role": "system", "content": "You are an empathetic AI coach. Acknowledge the user's emotion and provide a supportive, encouraging response."},
            {"role": "user", "content": f"The user is feeling {detected_emotion} about their assignments. Respond with empathy and encouragement."}
        ],
        stream=True  # Enable streaming
    )
    
    # Process the stream
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content, end='', flush=True)
    print()  # Add newline at the end

def collect_assignment_info(is_first_assignment=True):
    """
    Main function to collect assignment information from the user.
    Handles input of multiple assignments and returns collected data.
    
    Returns:
        list: List of dictionaries containing assignment information
    """
    assignments = []
    assignment_data = {
        "name": None,
        "due date": None,
        "due time": None,
        "time_allocated": None,
        "sessions": None
    }
    
    # Get and process initial response
    user_input = get_initial_assignment_info(is_first_assignment)  # Pass the flag
    missing_fields = process_assignment_dialogue(user_input, assignment_data)
    
    # Handle follow-ups if needed
    if missing_fields:
        handle_missing_info(missing_fields, assignment_data)
    
    # Add to assignments list
    assignments.append(assignment_data)
    
    # Ask about another assignment
    slow_print("\nWould you like to add another exam or assignment? (yes/no): ")
    another = input().lower()
    if another in ['y', 'yes']:
        assignments.extend(collect_assignment_info(False)) # Recursive call with is_first_assignment=False
    
    return assignments
