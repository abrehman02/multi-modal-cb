from openai import OpenAI
import base64
import chainlit as cl
import os

# Make sure to securely store the API key. Use an environment variable or a config file.
os.environ['OPENAI_API_KEY'] = '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'

# Initialize OpenAI client with API key
client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

def append_messages(image_url=None, query=None, audio_transcript=None):
    # Prepare a list of messages to send to the model
    message_list = []

    if image_url:
        message_list.append({"role": "user", "content": f"Image URL: {image_url}"})

    if query and not audio_transcript:
        message_list.append({"role": "user", "content": query})

    if audio_transcript:
        message_list.append({"role": "user", "content": query + "\n" + audio_transcript})

    # Make the API call to OpenAI
    response = client.chat.completions.create(
        model="gpt-4",  # Check the correct model name; use "gpt-4" or another supported model
        messages=message_list,
        max_tokens=1024,
    )

    # Return the content of the response
    return response.choices[0].message['content']

def image2base64(image_path):
    with open(image_path, "rb") as img:
        encoded_string = base64.b64encode(img.read())
    return encoded_string.decode("utf-8")

def audio_process(audio_path):
    with open(audio_path, "rb") as audio_file:
        # Use OpenAI's Whisper model to transcribe the audio
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    return transcription['text']

@cl.on_message
async def chat(msg: cl.Message):
    # Extract images and audios from the incoming message
    images = [file for file in msg.elements if "image" in file.mime]
    audios = [file for file in msg.elements if "audio" in file.mime]

    image_url = None
    text = None

    if len(images) > 0:
        # Convert the first image to Base64 and prepare a data URL
        base64_image = image2base64(images[0].path)
        image_url = f"data:image/png;base64,{base64_image}"

    if len(audios) > 0:
        # Process the first audio file to get its transcription
        text = audio_process(audios[0].path)

    response_msg = cl.Message(content="")

    # Determine the type of response based on the input received
    if len(images) == 0 and len(audios) == 0:
        response = append_messages(query=msg.content)

    elif len(audios) == 0:
        response = append_messages(image_url=image_url, query=msg.content)

    else:
        response = append_messages(query=msg.content, audio_transcript=text)

    # Set and send the response back to the user
    response_msg.content = response
    await response_msg.send()
