import os
import time
import requests
from openai import OpenAI

# ---------------------------------------------------------
# CONFIGURATION & ENVIRONMENT VARIABLES
# ---------------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
INSTAGRAM_USER_ID = os.getenv("INSTAGRAM_USER_ID")

client = OpenAI(api_key=OPENAI_API_KEY)

def generate_ai_image_and_caption(prompt_topic):
    print(f"🤖 Generating AI Image for: {prompt_topic}...")
    
    # 1. Image Generation via DALL-E 3
    img_response = client.images.generate(
        model="dall-e-3",
        prompt=f"A vibrant, highly detailed social media post background image about: {prompt_topic}",
        n=1,
        size="1024x1024"
    )
    image_url = img_response.data[0].url

    # 2. Caption Generation via GPT-4o
    print("✍️ Writing Instagram Caption...")
    text_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": f"Write an engaging Instagram caption with trending hashtags for a post about: {prompt_topic}"}
        ]
    )
    caption = text_response.choices[0].message.content

    return image_url, caption

def publish_to_instagram(image_url, caption):
    print("🚀 Connecting to Instagram API...")
    
    # Step A: Create Media Container
    container_url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_USER_ID}/media"
    payload = {
        'image_url': image_url,
        'caption': caption,
        'access_token': META_ACCESS_TOKEN
    }
    
    res = requests.post(container_url, data=payload)
    result = res.json()
    
    if "id" not in result:
        print("❌ Error Creating Container:", result)
        return False
        
    creation_id = result["id"]
    print(f"✅ Media Container Created (ID: {creation_id}). Waiting for processing...")
    
    # Instagram requires a small delay to process image URL
    time.sleep(10)

    # Step B: Publish Container
    publish_url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_USER_ID}/media_publish"
    pub_payload = {
        'creation_id': creation_id,
        'access_token': META_ACCESS_TOKEN
    }
    
    pub_res = requests.post(publish_url, data=pub_payload)
    pub_result = pub_res.json()

    if "id" in pub_result:
        print(f"🎉 SUCCESS! Post Published to Instagram. Post ID: {pub_result['id']}")
        return True
    else:
        print("❌ Publishing Failed:", pub_result)
        return False

if __name__ == "__main__":
    # Apne hisab se topic change karein
    topic = "Future of Artificial Intelligence in daily life"
    
    img_url, post_caption = generate_ai_image_and_caption(topic)
    publish_to_instagram(img_url, post_caption)
