import os
import json
import base64
from openai import OpenAI

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

client = OpenAI(
    api_key="-------------------------------------",   # Please use your own valid API Key
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

json_file_path = 'Please enter the address of your test json file'
image_base_path = 'Please enter the address of your test image'

# Read the JSON file
with open(json_file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

start_index = 0
for i, item in enumerate(data):
    if item.get("question_id") == 10001:  # Please fill in according to the actual format of the JSON file.
        start_index = i
        break

# Iterate over each question in the json file
for item in data[start_index:]:
    question = item.get("question")
    image_name = item.get("image")

    if not question or not image_name:
        continue

    image_path = os.path.join(image_base_path, image_name)

    if not os.path.exists(image_path):
        print(f"Image not found: {image_path}")
        item['answer'] = 'Image not found.'
        continue

    # Getting the base64 string
    base64_image = encode_image(image_path)

    try:
        completion = client.chat.completions.create(
            model="qwen-vl-max",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": f"data:image/jpeg;base64,{base64_image}"
                        },
                        {
                            "type": "text",
                            "text": question
                        }
                    ]
                }
            ]
        )
        answer = completion.choices[0].message.content
        item['answer'] = answer
        print(f"Question ID {item['question_id']} processed successfully.")
    except Exception as e:
        print(f"An error occurred while processing question ID {item['question_id']}: {e}")
        item['answer'] = f"Error: {e}"

# Write the updated data back to the JSON file
with open(json_file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Processing complete.")
