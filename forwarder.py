from telethon import TelegramClient, types
import os, asyncio, time
from dotenv import load_dotenv
import logging

load_dotenv()
session_string = os.getenv("SESSION_STRING")
bot_token = os.getenv("BOT_TOKEN")
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")

group_username = 'gudangpilemsubtitleindo' # group gudangn subtitle indonesia
user_to = 'seriusinibot' # ini bot yang mau store file id.


# Create the Telegram client
client = TelegramClient("iuploadyou", api_id, api_hash)

# async def list_dialogs():
#     await client.start()
#     async for dialog in client.iter_dialogs():
#         print(f"Name: {dialog.name}, ID: {dialog.id}")


# async def send_video(document: types.InputDocument):
#     return await client.send_message(
#         dummy_group, message='text_message', file=document, link_preview=True, supports_streaming=True
#     )

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')


async def main():
    await client.start()

    async def send_video(document: types.InputDocument, message: str):
        return await client.send_message(
            user_to, message=message, file=document, link_preview=True, supports_streaming=True
        )

    # Get the group entity
    group = await client.get_entity(group_username)
    # print(group)


    try:
        # Fetch the last message from the group
        last_message = await client.get_messages(group, limit=1)  # Get the most recent message

        if last_message:
            print(f"Last Message ID: {last_message[0].id}")
            for i in range(last_message[0].id):
                message = await client.get_messages(group, ids=i+1)
                i+=1

                # List to hold video IDs and access hashes
                video_info = []

                # print(message, '\n')
                # print('true' if message else 'not true')
                if message:
                    print('\n')
                    # print(message.to_dict())
                    try:
                        print('ok' if message.video or message.media else 'not ok')

                        try:
                            # print(message.to_dict())
                            # Get video ID and access hash
                            video_id = message.media.document.id
                            access_hash = message.media.document.access_hash
                            file_reference = message.media.document.file_reference
                            document = types.InputDocument(
                                id=video_id, access_hash=access_hash, file_reference=file_reference
                            )

                            text = message.message

                            filename = ''
                            for attribute in message.media.document.attributes:
                                if attribute.to_dict()['_'] == 'DocumentAttributeFilename':
                                    filename = attribute.to_dict()['file_name']


                            print(filename, text)
                            await send_video(document, text)
                            video_info.append((video_id, access_hash))
                            # print(f"Video ID: {video_id}, Access Hash: {access_hash}")


                            # input()
                        except Exception as e:
                            logging.warning(e)
                    except:continue
                    time.sleep(3)

                # print(message)
                # input()
                # Iterate through the messages in the group
                # async for message in client.iter_messages(group):
                # print(message.to_dict())
                # if message:
                #     if message.media and message.video:
                #         try:
                #             print(message.to_dict())
                #             # Get video ID and access hash
                #             video_id = message.media.document.id
                #             access_hash = message.media.document.access_hash
                #             file_reference = message.media.document.file_reference
                #             document = types.InputDocument(
                #                 id=video_id, access_hash=access_hash, file_reference=file_reference
                #             )

                #             filename = ''
                #             for attribute in message.media.document.attributes:
                #                 if attribute.to_dict()['_'] == 'DocumentAttributeFilename':
                #                     filename = attribute.to_dict()['file_name']


                #             # await send_video(document)
                #             # video_info.append((video_id, access_hash))
                #             # print(f"Video ID: {video_id}, Access Hash: {access_hash}")

                #             print(filename)

                #             input()
                #         except Exception as e:
                #             ic(e)
        
        else:
            print("No messages found in the group.")

    except Exception as e:
        logging.warning(e)

    # Optionally, save the info to a file
    # with open("video_info.txt", "w") as f:
    #     for video_id, access_hash in video_info:
    #         f.write(f"Video ID: {video_id}, Access Hash: {access_hash}\n")

    # client.run_until_disconnected()


if __name__=="__main__":
    with client:
        client.loop.run_until_complete(main())