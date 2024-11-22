import json

# Iinput and output file paths
input_file = "empatheticdialogues_preprocessed_prepared_valid.jsonl"
output_file = "empatheticdialogues_chat_formatted_valid.jsonl"

with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
    for line in infile:
        entry = json.loads(line)
        
        # Convert each entry to chat format with explicit emotion labeling
        chat_entry = {
            "messages": [
                {"role": "user", "content": entry["prompt"]},
                {"role": "assistant", "content": f"Emotion: {entry['completion'].strip()}"}
            ]
        }
        
        # Write to output file in JSONL format
        json.dump(chat_entry, outfile)
        outfile.write('\n')
