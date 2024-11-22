from datasets import load_dataset
import json

def prepare_data(split_name, output_file):
    # Load the EmpatheticDialogues dataset from Hugging Face
    dataset = load_dataset("empathetic_dialogues", trust_remote_code=True)

    # Prepare the data for fine-tuning
    data = []
    for entry in dataset[split_name]:  
        prompt = f"User said: '{entry['utterance']}'"
        completion = f"Emotion: {entry['context']}"
        data.append({"messages": [
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": completion}
        ]})

    # Save the processed data as JSONL
    with open(output_file, "w") as f:
        for item in data:
            f.write(json.dumps(item) + "\n")

    print(f"Dataset has been saved in JSONL format to {output_file}")

    # After running this file using this command: python prepare_dataset.py, 
    # Run this command: openai tools fine_tunes.prepare_data -f empatheticdialogues_preprocessed.jsonl to prepare the data for fine-tuning,
    # Answer Y to all the questions asked, and the data will be split to train and validation sets.

    # After running the above command, upload the files to the OpenAI platform to fine-tune the model by running the following command:
    # openai api files.create -f "replace this with".jsonl -p fine-tune
