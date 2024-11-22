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

# TO DELETE (Sample prompts for demo):
# I have a speech to prep for which is on monday at 9 am, I need to study for it for 6 hours over 3 sessions
# I have an AI assignment due on Saturday at 6PM which I want to work on for 4 hours over 1 session
# I have an assignment called challenge 7 due on Monday at 9PM, I want to work on it for 6 hours over 3 sesisons
# I have a book report to complete on tuesday by midnight, I want to study it over 1 large study session 8 hours long


# Simply run the file to interact with CollegeCoach!
if __name__ == "__main__":
    collegeCoachAI()