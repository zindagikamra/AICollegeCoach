import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

# Fine-tune model
fine_tune_response = openai.fine_tuning.jobs.create(
    model="gpt-4o-mini-2024-07-18",
    training_file="file-YTuM53fhq6UQIbOqhrCCAuk3",
    validation_file="file-7cCYwFyQCd0zTmUTBMqmM7Z5",
    suffix="AICollegeCoach_Model",
)

# Access the ID attribute
print(f"Fine-tuning job started with ID: {fine_tune_response.id}")

# Fetch and print job status
job_status = openai.fine_tuning.jobs.retrieve("ftjob-yCy8KgUcxnASCbKKQOPuPrGV")
print(f"Job Status: {job_status.status}")