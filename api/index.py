import os
import time
import requests
from openai import OpenAI
from http.server import BaseHTTPRequestHandler

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
INSTAGRAM_USER_ID = os.getenv("INSTAGRAM_USER_ID")

client = OpenAI(api_key=OPENAI_API_KEY)

def generate_and_post():
    topic = "Future of Artificial Intelligence in daily life"
    
    # 1. Image Generation
    img_response = client.images.generate(
        model="dall-e-3",
        prompt=f"A vibrant social media post image about: {topic}",
        n=1,
        size="1024x1024"
    )
    image_url = img_response.data[0].url

    # 2. Caption Generation
    text_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": f"Write an engaging Instagram caption with hashtags for: {topic}"}
        ]
    )
    caption = text_response.choices[0].message.content

    # 3. Publish to Instagram
    container_url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_USER_ID}/media"
    payload = {
        'image_url': image_url,
        'caption': caption,
        'access_token': META_ACCESS_TOKEN
    }
    
    res = requests.post(container_url, data=payload)
    result = res.json()
    
    if "id" not in result:
        return f"Error creating container: {result}"
        
    creation_id = result["id"]
    time.sleep(10)

    publish_url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_USER_ID}/media_publish"
    pub_payload = {
        'creation_id': creation_id,
        'access_token': META_ACCESS_TOKEN
    }
    
    pub_res = requests.post(publish_url, data=pub_payload)
    pub_result = pub_res.json()

    if "id" in pub_result:
        return f"SUCCESS! Published Post ID: {pub_result['id']}"
    else:
        return f"Publishing failed: {pub_result}"

# Vercel Serverless Function Handler
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        output = generate_and_post()
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(output.encode('utf-8'))
