import os, io
import re
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

# from telethon.utils import pack_bot_file_id
# from imdb import get_movie_data

# Load environment variables
load_dotenv()
bot_token = os.getenv("BOT_TOKEN")
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")

admin_user = "u_p_l_o_a_d_e_r"
SECRET_KEY = ""


# Initialize the Telegram client
client = TelegramClient("seriusinibot", api_id, api_hash)

def make_filename_safe(filename: str, divider: str) -> str:
    safe_name = re.sub(r"[^a-zA-Z0-9]", divider, filename)
    safe_name = re.sub(r"-+", "-", safe_name).strip("-")
    return safe_name

# Function to create a JWT
def create_jwt(data):
    expiration = datetime.datetime.utcnow() + datetime.timedelta(seconds=60)
    token = jwt.encode(data, SECRET_KEY, algorithm="HS256")
    return token

# Function to read (decode) a JWT
def read_jwt(token):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded
    except jwt.ExpiredSignatureError:
        return "Token has expired"
    except jwt.InvalidTokenError:
        return "Invalid token"


@client.on(events.NewMessage())
async def handler(event):
    # Check if the incoming message contains a video or document
    if event.message.video or event.message.document:
        datas = {}
        document = event.message.document

        # Initialize filename variable
        filename = None

        # Store document ID and access_hash in datas
        if document.id:
            datas["id"] = document.id

        if document.access_hash:
            datas["access_hash"] = document.access_hash

        # Loop through the document attributes to find the filename
        for attribute in document.attributes:
            if isinstance(attribute, DocumentAttributeFilename):
                filename = attribute.file_name
                break

        if filename:
            print(f"Filename: {filename}")
            datas["filename"] = filename

        else:
            print("No filename found in the document attributes.")

        print('\n')
        print(datas)

if __name__ == "__main__":
    with client:
        print("Listening for incoming messages...")
        client.run_until_disconnected()
