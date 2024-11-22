import openai
import os

# Set your API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Fine-tune job ID
fine_tune_job_id = "ftjob-yCy8KgUcxnASCbKKQOPuPrGV"  

# Retrieve and print job events
events = openai.fine_tuning.jobs.list_events(fine_tune_job_id)
for event in events.data:
    print(event.message)

# Fetch and print job status
job_status = openai.fine_tuning.jobs.retrieve(fine_tune_job_id)
print(f"Job Status: {job_status.status}")