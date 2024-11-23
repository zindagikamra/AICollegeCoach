from scheduler_logic import authorization, getOrAccessCoachCalendar, dedicateAssignmentTimes
from assignment_dialogue import collect_assignment_info, handle_emotional_checkin

def collegeCoachAI():
    # Initial login and creation or fetch of CollegeCoach Calendar
    service = authorization()
    calendar_id = getOrAccessCoachCalendar(service)

    # Get the assignment info from a student that they want to schedule slots for and make a schedule from it
    assignments = collect_assignment_info()
    dedicateAssignmentTimes(service, calendar_id, assignments)
    
    handle_emotional_checkin()

# Simply run the file to interact with CollegeCoach!
if __name__ == "__main__":
    collegeCoachAI()