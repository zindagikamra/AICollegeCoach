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


def slow_print(text, delay=0.01):
    """
    Prints out output of text decision with slight delay to emulate chatbot style
    
    Args:
        text (string): String to be printed with the delay
        delay (float): delay at which to print the characters of the given text (ms)
    """
    for char in text:
       print(char, end='', flush=True) 
       time.sleep(delay)
    print()


def create_unavailable_events(service, calendar_id):
   """
    Creates unavailable calendar based on user input
    
    Args:
        service (string): Resource object for interacting with Google's calendar API
        calendar_id (string): id of calendar to write to
    """
   days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


   slow_print("Since you are creating a new calendar, please enter times you cannot study. Use this for times when you are sleeping or away.")
   slow_print("Please enter your information by the following example format for the prompted day: 8:15AM-12:30PM, 1:00PM-3:00PM")


   for day in days_of_week:
       # Get unavailable times for the day from the user
       slow_print(f"Enter unavailable times for {day}: ")
       time_slots = input()
       unavailable_slots = parse_time_slots(time_slots)


       slow_print(f"Creating events for {day}")
       # Create recurring events for each unavailable time slot
       create_recurrence_events(service, calendar_id, day[:2].upper(), unavailable_slots)


def create_event(service, calendar_id, start_datetime, end_datetime, day):
    """
    Helper function to create a unavailable event
    
    Args:
        service (string): Resource object for interacting with Google's calendar API
        calendar_id (string): id of calendar to write to
        start_datetime (datetime): start time of event being made
        end_datetime (datetime): end time of event being made
        day (string): formatted string representing the day of the week an event should be on
    """
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
    service.events().insert(calendarId=calendar_id, body=event).execute()
    slow_print(f"Created event from {start_datetime} to {end_datetime} for {day}")


def create_recurrence_events(service, calendar_id, day, unavailable_slots):
   """
    Creates reoccuring events with the given information
    
    Args:
        service (string): Resource object for interacting with Google's calendar API
        calendar_id (string): id of calendar to write to
        day (string): formatted string representing the day of the week an event should be on
        unavailable_slots ([string]): array of formatted strings holding the time slots for the unavailable times
    """
   # Get the current date and weekday
   today = datetime.date.today()
   today_weekday = today.weekday()  # Monday=0, Sunday=6
   target_weekday = ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU'].index(day)


   # Calculate the difference in days
   days_ahead = (target_weekday - today_weekday) % 7
   date_of_slots = today if days_ahead == 0 else today + datetime.timedelta(days=days_ahead)


   for start, end in unavailable_slots:
        # If the event spans across midnight, split into two events
        if start > end:
            # First event: from start_time to midnight of the current day
            start_datetime = datetime.datetime.combine(date_of_slots, start)
            end_datetime = datetime.datetime.combine(date_of_slots, datetime.time(23, 59))
            create_event(service, calendar_id, start_datetime, end_datetime, day)

            # Second event: from midnight to end_time of the next day
            next_day = date_of_slots + datetime.timedelta(days=1)
            start_datetime = datetime.datetime.combine(next_day, datetime.time(0, 0))
            end_datetime = datetime.datetime.combine(next_day, end)
            next_day_name = ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU'][(target_weekday + 1) % 7]
            create_event(service, calendar_id, start_datetime, end_datetime, next_day_name)
        else:
            # Normal event creation
            start_datetime = datetime.datetime.combine(date_of_slots, start)
            end_datetime = datetime.datetime.combine(date_of_slots, end)
            create_event(service, calendar_id, start_datetime, end_datetime, day)


def create_study_event(service, calendar_id, assignment_name, start_time, end_time):
   """
    Creates a study event for the given time slot (creates singular non repeating event)
    
    Args:
        service (string): Resource object for interacting with Google's calendar API
        calendar_id (string): id of calendar to write to
        assignment_name (string): name of the assignment which's slots are being created
        start_datetime (datetime): start time of event being made
        end_datetime (datetime): end time of event being made
    """
   start_time_utc = start_time.replace(tzinfo=datetime.timezone.utc)
   end_time_utc = end_time.replace(tzinfo=datetime.timezone.utc)
  
   event = {
       'summary': f'Study for {assignment_name}',
       'start': {
           'dateTime': start_time_utc.isoformat(),
           'timeZone': 'UTC',
       },
       'end': {
           'dateTime': end_time_utc.isoformat(),
           'timeZone': 'UTC',
       },
       'colorId': 3,
   }
  
   try:
       service.events().insert(calendarId=calendar_id, body=event).execute()
   except HttpError as error:
       print(f"An error occurred: {error}")


def parse_time_slots(time_slots):
    """
    Parses passed time slots for blocking unavailable times and converts them into an array for blocking out events
    
    Args:
        time_slots (string): time slots entered in a specific format to be converted into unavailable times
    """
    pattern = r'(\d{1,2}:\d{2}[AP]M)-(\d{1,2}:\d{2}[AP]M)'

    while True:
        time_ranges = re.findall(pattern, time_slots)

        if time_ranges:
            parsed_slots = []
            for start, end in time_ranges:
                start_time = datetime.datetime.strptime(start, "%I:%M%p").time()
                end_time = datetime.datetime.strptime(end, "%I:%M%p").time()

                if start_time >= end_time: 
                    # Split into two segments: start to midnight, midnight to end
                    parsed_slots.append((start_time, datetime.time(23, 59)))  
                    parsed_slots.append((datetime.time(0, 0), end_time))     
                else:
                    parsed_slots.append((start_time, end_time)) 

            return parsed_slots
        else:
            slow_print("Incorrect format. Please enter the times in the correct format (e.g., 8:15AM-12:30PM, 1:00PM-3:00PM).")
            slow_print("Enter unavailable times: ")
            time_slots = input()



def getOrAccessCoachCalendar(service):
   """
    Finds stored coach calendar from the local calendar id file and if none located, then creates a new one.
    
    Args:
        service (string): Resource object for interacting with Google's calendar API
    """
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



def authorization():
   """
   Handles login and calendar access setup
   """
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


def print_scheduled_events(service, calendar_id):
   """
    Prints out all scheduled events
    
    Args:
        service (string): Resource object for interacting with Google's calendar API
        calendar_id (string): id of calendar to write to
    """
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



def get_unavailable_times(service, calendar_id):
   """
    Helper function to get unavailable times from the calendar
    
    Args:
        service (string): Resource object for interacting with Google's calendar API
        calendar_id (string): id of calendar to write to
    """
   now = datetime.datetime.utcnow().isoformat() + 'Z'
   then = (datetime.datetime.utcnow() + datetime.timedelta(days=30)).isoformat() + 'Z'
  
   events_result = service.events().list(calendarId=calendar_id, timeMin=now,
                                         timeMax=then, singleEvents=True,
                                         orderBy='startTime').execute()
   events = events_result.get('items', [])
   unavailable_times = []
  
   # Parse all unavailable times
   for event in events:
       start = event['start'].get('dateTime', event['start'].get('date'))
       end = event['end'].get('dateTime', event['end'].get('date'))
       start_dt = datetime.datetime.fromisoformat(start.rstrip('Z'))
       end_dt = datetime.datetime.fromisoformat(end.rstrip('Z'))
       start_dt = start_dt.replace(tzinfo=None)  # Remove timezone info
       end_dt = end_dt.replace(tzinfo=None)  # Remove timezone info
       unavailable_times.append((start_dt, end_dt))
   return unavailable_times
  


def schedule_session(service, calendar_id, name, current_time, session_duration, unavailable_times):
   """
    Helper function to schedule a single session
    
    Args:
        service (string): Resource object for interacting with Google's calendar API
        calendar_id (string): id of calendar to write to
    """
   while True:
       session_end_time = current_time + datetime.timedelta(minutes=session_duration)
       can_schedule = True


       for start, end in unavailable_times:
           if (current_time >= start and current_time < end) or \
              (session_end_time > start and session_end_time <= end) or \
              (current_time <= start and session_end_time >= end):
               can_schedule = False
               current_time = end  # Move to the end of the unavailable slot
               break


       if can_schedule:
           create_study_event(service, calendar_id, name, current_time, session_end_time)
           return session_end_time


       # If we can't schedule, we've moved current_time to the next available slot
       # and will try again in the next iteration



def dedicateAssignmentTimes(service, calendar_id, assignments):
   """
    Main function to dedicate assignment times
    
    Args:
        service (string): Resource object for interacting with Google's calendar API
        calendar_id (string): id of calendar to write to
        assignments ([obj]): array of assignment objects to convert into calendar blocked study sessions
    """
   unavailable_times = get_unavailable_times(service, calendar_id)
   assignments.sort(key=lambda x: x['due date'])
   current_time = datetime.datetime.now().replace(tzinfo=None, microsecond=0)
   current_time = current_time.replace(minute=0, second=0) + datetime.timedelta(hours=1)

   for assignment in assignments:
       name = assignment['name']
       due_date = datetime.datetime.combine(assignment['due date'], assignment['due time'])
       total_minutes = assignment['time_allocated']
       sessions = assignment['sessions']
       session_duration = total_minutes // sessions


       slow_print(f"Scheduling {name} due on {due_date}")


       # Calculate available time slots and ideal spacing
       time_until_due = due_date - current_time
       if time_until_due.total_seconds() <= 0:
           slow_print(f"Warning: The due date for {name} has already passed.")
           continue


       # Calculate ideal interval between sessions
       interval_hours = time_until_due.total_seconds() / (3600 * (sessions + 1))


       # Schedule each session
       scheduled_sessions = 0
       while scheduled_sessions < sessions:
           # Calculate the ideal start time for this session
           target_time = current_time + datetime.timedelta(hours=interval_hours * (scheduled_sessions + 1))


           # Find the next available slot close to the target time
           start_time = max(current_time, target_time)
           while start_time <= due_date:
               session_end_time = start_time + datetime.timedelta(minutes=session_duration)


               # Check if the time slot is available
               if all(start_time >= end or session_end_time <= start for start, end in unavailable_times):
                   # Schedule the session
                   create_study_event(service, calendar_id, name, start_time, session_end_time)
                   unavailable_times.append((start_time, session_end_time))
                   unavailable_times.sort(key=lambda x: x[0])
                   scheduled_sessions += 1
                   break


               # Try the next 15-minute slot
               start_time += datetime.timedelta(minutes=15)


               # Roll over to the next day if needed
               if start_time.time() > datetime.time(23, 45):
                   start_time = start_time.replace(hour=0, minute=0) + datetime.timedelta(days=1)


           # If no valid slot was found before the due date, log a warning
           if start_time > due_date:
               slow_print(f"Warning: Could not schedule all sessions for {name} before the due date.")
               break


       slow_print(f"Finished scheduling {name}")