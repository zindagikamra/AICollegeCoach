# AICollegeCoach: An AI Powered Assignment Scheduler and Emotional Support Coach

## Overview
This project utilizes a fine-tuned gpt-4o-mini-2024-07-18 model, along with the Google Calendar API to make a chat bot which is able to take user input according to their assignment descriptions and convert them into an optimized scheduler while also holding functionality to respond to the user's emotional state with enhanced ability due to its refined emotion detection. The project is interacted with by running it within the terminal.

## Features

- #### Optimized Schedule Creation
    The project allows users to input as many assignments as they want in a go with assignment details such as a name, due date and time, and the amount of them they want to work on it. It then uses this information to create an optimized schedule using a greedy algorithm according to due times, trying to schedule study blocks as early as possible from the users' available times to make sure they have ample time to complete their assignments. This also contributes to the emotional component as this scheduling leads to the least possible stress from workload as possible.

- #### Assignment Description Processing
    Using the GPT-4 basic model, we enable our project to allow the user to enter their assignment details in causal language and with relative terms such as "next Tuesday" as opposed to having to provide specific dates. We then ask the model to convert this into a pre-decided json format for our scheduler algorithm to receive and convert into the optimal schedule. This ensures ease of use on the users' part while maintaining smooth program operation

- #### Emotional Response
    The fine-tuned model (gpt-4o-mini-2024-07-18 model) is utilized to detect the emotion the user inputs when asked about how they are feeling about their workload. This model uses its detected emotion, passes it to the general model and asks it to generate a response which will offer emotional support to the user. It encourages them if they feel good and gives them words of reassurance if not.

## Document Overview
- requirements.txt: Hold the model requirements for download to make the program function as intended.
- assignment_dialogue.py: Holds the logic for the assignment input interaction, leading into the emotional prompt. It utilizes both the refined GPT model and the regular.
- check_fine_tune_status.py: Holds logic to check status of fine tuner as it is executing.
- college_coach.py: Combines scheduler_logic and assignment_dialogue methods into a working project flow. Once setup is complete, this is the only file which needs to be run in order to use the project.
- fine_tune.py: Holds logic to execute fine-tuning job.
- prepare_dataset.py: Holds logic to format dataset before training model with it.
- preprocess_dataset.py: Converts the dataset to a OpenAI understandable format before it is prepared and processed.
- scheduler_logic.py: Holds the logic for all interactions with the Google Calendar API. Due to this, the file contains logic for google login, unavailable time allocation, and the scheduler logic.
- testing_model.py: Runs the code to test the fine-tuned gpt model and its accuracy across different metrics and the untrained model.

## Getting Started

### Prerequisites
Before executing the program, it is important to have these requirements fufilled:
  - Python 3.11+
  - google-auth-oauthlib>=0.4.6
  - google-auth>=2.22.0
  - google-api-python-client>=2.0.0
  - openai==1.54.4
  - python-dotenv==1.0.1
  - datasets
  - google-auth-httplib2
  - scikit-learn
  - pandas

To get the authorization tokens for the used APIs, please visit and follow the documentation below:
  - Google Calendar API: https://developers.google.com/workspace/guides/configure-oauth-consent
  - OpenAI API: https://openai.com/api/pricing/

### Installation
In order to download all the needed dependencies and run the program, please follow the steps below:

  1. Choose a location to clone your github repo and run this command:
     
    git clone git@github.com:<YOUR_USERNAME>/AICollegeCoach.git

  2. Navigate into your cloned directory and run the following command to download all dependencies:
  
    pip install -r requirements.txt

  3. Once you have all of the needed tokens and dependencies, run the following command to train the models:

    COMMAND(S) FOR TRAINING MODEL
    
  4. Finally, once the model is trained, run the following command to launch the college coach:

    python college_coach.py

  OR
  
    python3 college_coach.py

## Model and Tokenizer
The tokens created for the Google Calendar API should be stored in a config.json file which should be in the same directory as scheduler_logic.py. The .env file should have the following format:
    
    OPENAI_MODEL_NAME='gpt-4o-mini'
    OPENAI_API_KEY='YOUR_KEY'
    OPENAI_FINETUNED_MODEL='YOUR_FINETUNED_MODEL_ID'

## Acknowledgments and Resources
This project utilizes the following datasets, APIs, and Models:

  - Empathetic Dialogue Dataset (https://github.com/facebookresearch/EmpatheticDialogues): Used to fine-tune emotion detection of gpt-4o-mini-2024-07-18 model.
  - Google Calendar API (https://developers.google.com/calendar/api/guides/overview): Used to set up coach calendar and create study/ unavailable events.
  - OpenAI Models (Regular: https://platform.openai.com/docs/api-reference/introduction): Used for assignment description parsing and emotion based response generation.
  - OpenAI Models (Fine-tuned: https://platform.openai.com/docs/api-reference/fine-tuning): Refined gpt-4o-mini-2024-07-18 model used for emotion detetion from user input.
