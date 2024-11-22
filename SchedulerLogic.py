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
# Finds all available time slots on a given date
def get_available_slots(service, calendar_id, date):
    # Set the time range for the day
    start_time = datetime.datetime.combine(date, datetime.time.min).isoformat() + 'Z'
    end_time = datetime.datetime.combine(date, datetime.time.max).isoformat() + 'Z'

    # Retrieve events for the specified day
    events_result = service.events().list(calendarId=calendar_id, timeMin=start_time,
                                          timeMax=end_time, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    # Initialize available slots with full day
    available_slots = [(datetime.datetime.combine(date, datetime.time.min),
                        datetime.datetime.combine(date, datetime.time.max))]

    # Remove occupied time slots
    for event in events:
        start = datetime.datetime.fromisoformat(event['start'].get('dateTime', event['start'].get('date')))
        end = datetime.datetime.fromisoformat(event['end'].get('dateTime', event['end'].get('date')))

        new_available_slots = []
        for slot_start, slot_end in available_slots:
            if start <= slot_start and end >= slot_end:
                continue
            elif start > slot_start and end < slot_end:
                new_available_slots.append((slot_start, start))
                new_available_slots.append((end, slot_end))
            elif start > slot_start and start < slot_end:
                new_available_slots.append((slot_start, start))
            elif end > slot_start and end < slot_end:
                new_available_slots.append((end, slot_end))
            else:
                new_available_slots.append((slot_start, slot_end))
        available_slots = new_available_slots

    return available_slots

# NOT DONE YET
def dedicateAssignmentTimes(assignments, service, calendar_id):
    # Sort assignments by due date
    sorted_assignments = sorted(assignments, key=lambda x: (x['due date'], x['due time']))
    
    def backtrack(index):
        if index == len(sorted_assignments):
            return True  # All assignments scheduled successfully
        
        assignment = sorted_assignments[index]
        due_datetime = datetime.datetime.combine(assignment['due date'], assignment['due time'])
        session_duration = assignment['time_allocated'] // assignment['sessions']
        
        # Get available dates from today until the due date
        today = datetime.date.today()
        date_range = [today + datetime.timedelta(days=x) for x in range((assignment['due date'] - today).days + 1)]
        
        for date in date_range:
            available_slots = get_available_slots(service, calendar_id, date)
            
            for start, end in available_slots:
                slot_duration = (end - start).total_seconds() / 60
                
                if slot_duration >= session_duration:
                    # Try to schedule the session
                    session_end = start + datetime.timedelta(minutes=session_duration)
                    create_study_event(service, calendar_id, assignment['name'], start, session_end)
                    
                    # Recursively try to schedule the next assignment
                    if backtrack(index + 1):
                        return True
                    
                    # If scheduling fails, remove the event and try the next slot
                    # Note: In a real implementation, you'd need to add a function to delete the event
                    # delete_study_event(service, calendar_id, assignment['name'], start, session_end)
    
    if backtrack(0):
        slow_print("All assignments scheduled successfully!")
    else:
        slow_print("Unable to schedule all assignments. Please review your calendar and assignments.")

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

# prints out all scheduled events
def print_scheduled_events(service, calendar_id):
    # Get events from today to 30 days in the future
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    then = (datetime.datetime.utcnow() + datetime.timedelta(days=30)).isoformat() + 'Z'
    
    events_result = service.events().list(calendarId=calendar_id, timeMin=now,
                                          timeMax=then, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        slow_print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        slow_print(f"{event['summary']}: {start}")


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
    
    # Print scheduled events
    print_scheduled_events(service, calendar_id)

main()