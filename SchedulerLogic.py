import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import datetime
import time
import sys
import json
import re

SCOPES = ['https://www.googleapis.com/auth/calendar']

# GOOD
# Prints out output of text decision with slight delay to emulate chatbot style
def slow_print(text, delay=0.01):
    for char in text:
        print(char, end='', flush=True)  
        time.sleep(delay) 
    print()

#GOOD
# Creates unavailable calendar based on user input
def create_unavailable_events(service, calendar_id):
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    slow_print("Since you are creating a new calendar, please enter times you cannot study. Use this for times when you are sleeping or away.")
    slow_print("Please enter your information by the following example format for the prompted day: 8:15AM-12:30PM, 1:00PM-3:00PM")

    for day in days_of_week:
        # Get unavailable times for the day from the user
        time_slots = input(f"Enter unavailable times for {day}: ")
        unavailable_slots = parse_time_slots(time_slots)

        slow_print(f"Creating events for {day}")
        # Create recurring events for each unavailable time slot
        create_recurrence_events(service, calendar_id, day[:2].upper(), unavailable_slots)

# GOOD
# Creates reoccuring events with the given information
def create_recurrence_events(service, calendar_id, day, unavailable_slots):
    # Get the current date and weekday
    today = datetime.date.today()
    today_weekday = today.weekday()  # Monday=0, Sunday=6
    target_weekday = ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU'].index(day)

    # Calculate the difference in days
    days_ahead = (target_weekday - today_weekday + 7) % 7
    if days_ahead == 0:
        days_ahead = 7

    # Return the calculated date for the target weekday
    date_of_slots = today + datetime.timedelta(days=days_ahead)

    for start, end in unavailable_slots:
        # Combine date with time for event start and end (use today’s date as a placeholder)
        start_datetime = datetime.datetime.combine(date_of_slots, start)
        end_datetime = datetime.datetime.combine(date_of_slots, end)
        
        event = {
            'summary': 'Unavailable Time',
            'start': {
                'dateTime': start_datetime.isoformat(),
                'timeZone': 'America/New_York',
            },
            'end': {
                'dateTime': end_datetime.isoformat(),
                'timeZone': 'America/New_York',
            },
            'recurrence': [
                f'RRULE:FREQ=WEEKLY;BYDAY={day}'
            ],
        }
        
        # Insert the event into the specified calendar
        service.events().insert(calendarId=calendar_id, body=event).execute()
        slow_print(f"Creating event on {date_of_slots} from {start} to {end} for {day}")

# GOOD
# Creates a study event for the given time slot (creates singular non repeating event)
def create_study_event(service, calendar_id, assignment_name, start_time, end_time):
    """
    Creates a study event in the calendar for a specific assignment.
    """
    event = {
        'summary': f'Study for {assignment_name}',
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'America/New_York',
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': 'America/New_York',
        },
        'colorId': 3,
    }
    try:
        service.events().insert(calendarId=calendar_id, body=event).execute()
        #slow_print(f"Scheduled study session for {assignment_name} from {start_time} to {end_time}")
    except HttpError as error:
        print(f"An error occurred: {error}")

# GOOD
#Parses passed time slots for blocking unavailable times and converts them into an array for blocking out events
def parse_time_slots(time_slots):
    pattern = r'(\d{1,2}:\d{2}[AP]M)-(\d{1,2}:\d{2}[AP]M)'

    while True:
        time_ranges = re.findall(pattern, time_slots)
        
        if time_ranges and len(time_ranges) * 14 == len(time_slots.replace(" ", "").replace(",", "")):
            parsed_slots = []
            for start, end in time_ranges:
                start_time = datetime.datetime.strptime(start, "%I:%M%p").time()
                end_time = datetime.datetime.strptime(end, "%I:%M%p").time()
                if start_time >= end_time:
                    print(f"Error: Start time {start} should be before end time {end}.")
                    print("BROKE")
                    break
                parsed_slots.append((start_time, end_time))
            else:
                return parsed_slots
        else:
            slow_print("Incorrect format. Please enter the times in the correct format (e.g., 8:15AM-12:30PM, 1:00PM-3:00PM).")
            time_slots = input("Enter unavailable times: ")


# GOOD
# Finds stored coach calendar from the local calendar id file and if none located, then creates a new one.
def getOrAccessCoachCalendar(service):
    # Check if we already have a saved calendar ID
    calendar_id_file = 'calendar_id.json'
    if os.path.exists(calendar_id_file):
        with open(calendar_id_file, 'r') as f:
            calendar_id = json.load(f).get("calendar_id")
    else:
        # Create a new calendar if no file exists
        calendar = {
            'summary': 'AICollegeCoach Schedule',
            'timeZone': 'UTC'
        }
        created_calendar = service.calendars().insert(body=calendar).execute()
        calendar_id = created_calendar['id']

        # Save the calendar ID to a JSON file
        with open(calendar_id_file, 'w') as f:
            json.dump({"calendar_id": calendar_id}, f)

        #Since the calendar is new, prompt the user to block out unavailable times
        create_unavailable_events(service, calendar_id)
        slow_print("Saving newly created calendar...")

    # return the calendar id being used
    return calendar_id


# NOT DONE YET
def get_available_slots(service, calendar_id, date):
    print("Add logic here")

# NOT DONE YET
def dedicateAssignmentTimes(assignments, service, calendar_id):
    print("Add logic here")

# GOOD
# handles login and calendar access setup
def authorization():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('config.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)
    return service


def main():

    service = authorization()
    calendar_id = getOrAccessCoachCalendar(service)
    create_unavailable_events(service, calendar_id)
    
    assignments = [
    {
        "name": "Math Homework",
        "due date": datetime.date(2024, 11, 15),  
        "due time": datetime.time(23, 59),        
        "time_allocated": 240,                    
        "sessions": 4                             
    },
    # # {
    # #     "name": "Science Project",
    # #     "due date": datetime.date(2024, 11, 18),
    # #     "due time": datetime.time(17, 0),
    # #     "time_allocated": 180,                    
    # #     "sessions": 3                             
    # # },
    # # {
    # #     "name": "English Essay",
    # #     "due date": datetime.date(2024, 11, 20),
    # #     "due time": datetime.time(14, 30),
    # #     "time_allocated": 300,                    
    # #     "sessions": 5                             
    # # }
    ]

    # Call scheduler
    dedicateAssignmentTimes(assignments, service, calendar_id)
main()