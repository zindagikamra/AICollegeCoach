import openai
import os
import json
import re
from sklearn.metrics import classification_report, confusion_matrix
import pandas as pd

# Set the OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.organization = "cs4100"

# Load the validation dataset
with open("empatheticdialogues_chat_formatted_valid.jsonl") as f:
    validation_data = [json.loads(line) for line in f]

# Counter for correct predictions
correct_predictions = 0
total_predictions = 0
misclassified_samples = []

# Preprocess user message
def preprocess_user_message(message):
    # Normalize text (remove special characters, extra spaces, etc.)
    message = re.sub(r"_comma_", ",", message)
    message = re.sub(r"[^a-zA-Z0-9\s.,!?']", "", message)
    return message.strip()

# Emotion mapping for broader emotion
emotion_mapping = {
    # Positive
    "affectionate": "positive",
    "caring": "positive",
    "excited": "positive",
    "grateful": "positive",
    "hopeful": "positive",
    "joyful": "positive",
    "proud": "positive",
    "confident": "positive",
    "impressed": "positive",

    # Negative
    "afraid": "negative",
    "angry": "negative",
    "annoyed": "negative",
    "anxious": "negative",
    "apprehensive": "negative",
    "ashamed": "negative",
    "disappointed": "negative",
    "disgusted": "negative",
    "furious": "negative",
    "guilty": "negative",
    "jealous": "negative",
    "sad": "negative",
    "terrified": "negative",
    "embarrassed": "negative",

    # Neutral
    "content": "neutral",
    "faithful": "neutral",
    "nostalgic": "neutral",
    "prepared": "neutral",
    "sentimental": "neutral",
    "trusting": "neutral",
    "surprised": "neutral",
    "anticipating": "neutral",
    "lonely": "neutral",
    "devastated": "neutral",
}

# # Emotion Mapping
# emotion_mapping = {
#     # Sad
#     "lonely": "sad",
#     "nostalgic": "sad",
#     "disappointed": "sad",
#     "devastated": "sad",
#     "sad": "sad",
#     "sentimental": "sad",

#     # Fear
#     "afraid": "fear",
#     "anxious": "fear",
#     "apprehensive": "fear",
#     "terrified": "fear",

#     # Anger
#     "angry": "anger",
#     "annoyed": "anger",
#     "disgusted": "anger",
#     "furious": "anger",

#     # Joy
#     "content": "joy",
#     "excited": "joy",
#     "grateful": "joy",
#     "hopeful": "joy",

#     # Love
#     "affectionate": "love",
#     "caring": "love",

#     # Trust
#     "faithful": "trust",
#     "confident": "trust",
#     "proud": "trust",
#     "trusting": "trust",

#     # Surprise
#     "impressed": "surprise",
#     "surprised": "surprise",

#     # Shame
#     "ashamed": "shame",
#     "embarrassed": "shame",
#     "guilty": "shame",

#     # Envy
#     "jealous": "envy",

#     # Anticipation
#     "prepared": "anticipation",
#     "anticipating": "anticipation",
# }

# Map emotion to broader category
def map_emotion(emotion):
    return emotion_mapping.get(emotion.lower(), "unknown")

# Collect expected and predicted emotions
expected_emotions = []
predicted_emotions = []

# Iterate over a subset of the validation data
for sample in validation_data[:int(0.2 * len(validation_data))]:  # 20% of the validation data
    user_message = preprocess_user_message(sample["messages"][0]["content"])
    expected_emotion = sample["messages"][1]["content"].replace("Emotion: ", "").strip()
    mapped_expected_emotion = emotion_mapping.get(expected_emotion, expected_emotion)

    # Query to the fine-tuned model
    response = openai.chat.completions.create(
        model="ft:gpt-4o-mini-2024-07-18:personal:aicollegecoach-model:ASuxr3X3",
        messages=[
            {"role": "system", "content": "You are an assistant trained to detect emotions. Based on the user's message, respond with a single word that represents the detected emotion."},
            # For testing GPT-4o-mini purposes
            # {"role": "system", "content": """
            #     You are an assistant trained to detect emotions in user messages. 
            #     Based on the user's message, respond with exactly one of the following emotions: 
            #     affectionate, caring, excited, grateful, hopeful, proud, joyful, confident, impressed, 
            #     afraid, angry, annoyed, anxious, apprehensive, ashamed, disappointed, disgusted, furious, guilty, 
            #     jealous, sad, terrified, embarrassed, content, faithful, nostalgic, prepared, sentimental, trusting, 
            #     surprised, anticipating, lonely, devastated.

            #     Your response should be a single word from this list that best represents the emotion conveyed in the user's message.
            #     """},
            # {"role": "user", "content": user_message}
        ],
        max_tokens=10
    )

    # Extract the predicted emotion
    predicted_emotion = response.choices[0].message.content.strip().lower()
    mapped_predicted_emotion = emotion_mapping.get(predicted_emotion, "unknown").lower()

    # Append to lists for metrics calculation
    expected_emotions.append(mapped_expected_emotion.lower())
    predicted_emotions.append(mapped_predicted_emotion)

    # Check if prediction matches the expected emotion
    if mapped_predicted_emotion.lower() == mapped_expected_emotion.lower():
        correct_predictions += 1
    else:
        # Log misclassified sample details
        misclassified_samples.append({
            "user_message": user_message,
            "expected_emotion": expected_emotion,
            "predicted_emotion": predicted_emotion,
            "mapped_expected_emotion": mapped_expected_emotion,
            "mapped_predicted_emotion": mapped_predicted_emotion
        })
    total_predictions += 1

# Calculate accuracy
accuracy = (correct_predictions / total_predictions) * 100
print(f"Accuracy on validation subset: {accuracy:.2f}%")

# Classification report
print("\nClassification Report:")
print(classification_report(
    expected_emotions,  # y_true
    predicted_emotions,  # y_pred
    labels=list(set(expected_emotions)),  
    zero_division=0
))

# Confusion matrix
labels = list(set(expected_emotions))
conf_matrix = confusion_matrix(expected_emotions, predicted_emotions, labels=list(set(expected_emotions)))
conf_matrix_df = pd.DataFrame(conf_matrix, index=list(set(expected_emotions)), columns=list(set(expected_emotions)))
print("\nConfusion Matrix:")
print(conf_matrix_df)

# Display misclassified samples for analysis
print("\nMisclassified Samples:")
for sample in misclassified_samples:
    print(f"User Message: {sample['user_message']}")
    print(f"Expected Emotion: {sample['expected_emotion']} (Mapped: {sample['mapped_expected_emotion']})")
    print(f"Predicted Emotion: {sample['predicted_emotion']} (Mapped: {sample['mapped_predicted_emotion']})")
    print("-" * 40)

