import os, io
import re, json
import datetime
import jwt
import requests, aiohttp
import asyncio, tempfile
from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.tl.types import (
    InputDocument,
    InputFile,
    InputMediaPhotoExternal,
    DocumentAttributeFilename,
    InputChatPhoto,
    InputMediaPhoto,
    InputFile,
    Document,
    InputPhoto,
    InputWebDocument
)

dummy_data = {
    "title": "",
    "description": "",
    "imdb_id": "",
    "cover_url": "",
    "magnet_url": "",
    "is_uploaded": False,
    "video_id": "",
    "trailer_id": "",
    "filename": ""
}

load_dotenv()
bot_token = os.getenv("BOT_TOKEN")
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")

admin_user = "u_p_l_o_a_d_e_r"
SECRET_KEY = ""

session_name = "seriusinibot"
api_url = 'http://localhost:8001'

# Initialize the Telegram client
client = TelegramClient(session_name, api_id, api_hash)

def make_filename_safe(filename: str, divider: str):
    safe_name = re.sub(r"[^a-zA-Z0-9]", divider, filename)
    safe_name = re.sub(r"-+", "-", safe_name).strip("-")
    return safe_name

# Function to create a JWT
def create_jwt(data):
    expiration = datetime.datetime.utcnow() + datetime.timedelta(seconds=60)
    token = jwt.encode(data, session_name, algorithm="HS256")
    return token

# Function to read (decode) a JWT
def read_jwt(token):
    try:
        decoded = jwt.decode(token, session_name, algorithms=["HS256"])
        return decoded
    except jwt.ExpiredSignatureError:
        return "Token has expired"
    except jwt.InvalidTokenError:
        return "Invalid token"


@client.on(events.NewMessage())
async def handler(event):
    # Check if the incoming message contains a video or document
    if event.message.video or event.message.document:
        datas = dummy_data.copy()
        video_data = {}
        document = event.message.document

        # Initialize filename variable
        filename = None

        # Store document ID and access_hash in datas
        if document.id:
            video_data["id"] = document.id

        if document.access_hash:
            video_data["access_hash"] = document.access_hash

        # Loop through the document attributes to find the filename
        for attribute in document.attributes:
            if isinstance(attribute, DocumentAttributeFilename):
                filename = attribute.file_name
                break

        if filename:
            # print(f"Filename: {filename}")
            video_data["filename"] = filename
            datas['filename'] = filename

        else:
            print("No filename found in the document attributes.")


        video_id = create_jwt(video_data)
        title = make_filename_safe(datas.get('filename'), ' ').strip()

        datas['video_id'], datas['title'], datas['filename'] = video_id, title.title(), filename

        

        # print('\n')
        # print(f"Judulnya barangkali '{title}'")
        # print(datas)

        post_response = requests.post(f"{api_url}/items/", json=datas)
        post_response.raise_for_status()
        print(json.dumps(post_response.json(), indent=4))

if __name__ == "__main__":
    with client:
        print("Listening for incoming messages...")
        client.run_until_disconnected()
