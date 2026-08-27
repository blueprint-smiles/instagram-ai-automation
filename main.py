import os
import time
import requests
from openai import OpenAI
from flask import Flask, jsonify

app = Flask(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
INSTAGRAM_USER_ID = os.getenv("INSTAGRAM_USER_ID")

client = OpenAI(api_key=OPENAI_API_KEY)

@app.route('/', methods=['GET', 'POST'])
def run_automation():
    try:
        topic = "Future of Artificial Intelligence in daily life"
        
        # 1. Image Generation via DALL-E 3
        img_response = client.images.generate(
            model="dall-e-3",
            prompt=f"A vibrant social media post image about: {topic}",
            n=1,
            size="1024x1024"
        )
        image_url = img_response.data[0].url

        # 2. Caption Generation via GPT-4o
        text_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": f"Write an engaging Instagram caption with hashtags for: {topic}"}
            ]
        )
        caption = text_response.choices[0].message.content

        # 3. Step A: Create Media Container on Instagram
        container_url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_USER_ID}/media"
        payload = {
            'image_url': image_url,
            'caption': caption,
            'access_token': META_ACCESS_TOKEN
        }
        
        res = requests.post(container_url, data=payload)
        result = res.json()
        
        if "id" not in result:
            return jsonify({"status": "error", "message": "Container Creation Failed", "details": result}), 400
            
        creation_id = result["id"]
        time.sleep(10)

        # Step B: Publish to Instagram
        publish_url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_USER_ID}/media_publish"
        pub_payload = {
            'creation_id': creation_id,
            'access_token': META_ACCESS_TOKEN
        }
        
        pub_res = requests.post(publish_url, data=pub_payload)
        pub_result = pub_res.json()

        if "id" in pub_result:
            return jsonify({"status": "success", "post_id": pub_result['id'], "message": "Post Published!"}), 200
        else:
            return jsonify({"status": "error", "message": "Publishing Failed", "details": pub_result}), 400

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run()
