import asyncio
import re
import sqlite3
import struct
import subprocess
import time
import webbrowser
import eel
import datetime
import os
import pvporcupine
import pyaudio
import pyautogui
import pywhatkit as kit
import wikipedia
import requests
import chromadb
import psycopg
import ast
import speedtest
import google.generativeai as genai
from torch import torch, autocast
from diffusers import StableDiffusionPipeline, EulerDiscreteScheduler
from playsound import playsound
from tqdm import tqdm
from pipes import quote
from psycopg.rows import dict_row
from engine.command import speak
from engine.config import *
from engine.helper import download_and_play_youtube_audio, extract_yt_term, search_youtube, remove_words
import time
from tenacity import retry, stop_after_attempt, wait_exponential

conn = sqlite3.connect("aiassistant.db")
cursor = conn.cursor()

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

client = chromadb.Client()

system_prompt = (
  'You are an AI assistant named Aria that has memory of every conversation you have ever had with this user. '
  f'The user is named {USER}, is 21 years old, birthday 29/04/2003, and is Romanian. '
  'On every prompt from the user, the system has checked for any relevant messages you have had with the user. '
  'If any embedded previous conversations are attached, use them for context to responding to the user, '
  'if the context is relevant and useful to responding. If the recalled conversations are irrelevant, '
  'disregard speaking about them and respond normally as an AI assistant. Do not talk about recalling conversations. '
  'Just use any useful data from the previous conversations and respond normally as an intelligent AI assistant.'
)
conversation = [{'role': 'system', 'content': system_prompt}]

# Load Text-To-Image Model
model_id = "stabilityai/stable-diffusion-2-1-base"
scheduler = EulerDiscreteScheduler.from_pretrained(model_id, subfolder="scheduler")
pipe = StableDiffusionPipeline.from_pretrained(model_id, scheduler=scheduler, torch_dtype=torch.float16)
pipe = pipe.to("cuda")

@eel.expose
def play_assistant_sound():
  music_dir = "www\\assets\\audio\\start_sound.mp3"
  playsound(music_dir)

def open_command(query):
  query = query.replace(ASSISTANT_NAME, "")
  query = query.replace("open", "")
  query.lower()
  
  app_name = query.strip()

  if app_name != "":
    try:
      cursor.execute('SELECT path FROM sys_command WHERE name IN (?)', (app_name,))
      results = cursor.fetchall()
      print(results)

      if len(results) != 0:
        asyncio.run(speak("Opening " + query))
        os.startfile(results[0][0])
      elif len(results) == 0:
        cursor.execute('SELECT path FROM web_command WHERE name IN (?)', (app_name,))
        results = cursor.fetchall()

        if len(results) != 0:
          asyncio.run(speak("Opening " + query))
          webbrowser.open(results[0][0])
        else:
          asyncio.run(speak("Opening " + query))
          try:
            os.system('start ' + query)
          except:
            asyncio.run(speak("Not Found"))
    except Exception as e:
      asyncio.run(speak("Something went wrong"))
      print(e)

def set_volume(query):
    """
    Set the system volume based on a query such as:
    - "set volume to max"
    - "set volume to min"
    - "set volume to 50%"
    
    :param query: A string query to adjust the volume.
    """
    # Normalize the query to lowercase to make parsing easier
    query = query.lower()

    # Handle 'max' case
    if "max" in query:
        volume_percentage = 100
    # Handle 'min' case
    elif "min" in query:
        volume_percentage = 0
    # Handle percentage case (e.g., "set volume to 50%")
    else:
        # Use regex to find a percentage in the query
        match = re.search(r"(\d+)\s*%", query)
        if match:
            volume_percentage = int(match.group(1))
            # Clamp the value between 0 and 100 just in case
            volume_percentage = min(max(volume_percentage, 0), 100)
        else:
            print("Could not parse volume from query.")
            return
    
    # Set the volume based on the parsed percentage
    asyncio.run(speak(f"Setting the volume to {volume_percentage}%"))
    from engine.helper import set_system_volume
    set_system_volume(volume_percentage)

def play_youtube(query):
  search_term = extract_yt_term(query)
  asyncio.run(speak("Playing " + search_term + " on Youtube"))
  kit.playonyt(search_term)

def play_music(query):
  query = query.split("play", 1)[1].strip()
  url = search_youtube(query)
  asyncio.run(speak("Playing " + query))
  download_and_play_youtube_audio(url)

def get_time():
  now = datetime.datetime.now()
  current_time = now.strftime("%H:%M:%S")
  asyncio.run(speak(f"The current time is {current_time}"))

def get_internet_speed():
  try:
    speed = speedtest.Speedtest(secure=True)
    download_speed = speed.download() / 1048576  # Convert to Mbps
    upload_speed = speed.upload() / 1048576      # Convert to Mbps

    # Format to two decimal places
    message = (f"Your Internet download speed is {download_speed:.2f} Mbps, " f"and your upload speed is {upload_speed:.2f} Mbps.")
    asyncio.run(speak(message))
  except Exception as e:
    asyncio.run(speak(f"Error occurred while testing your internet speed: {str(e)}"))

def get_weather(query):
    if ("in" in query):
      city = query.split("in", 1)[1].strip()
    else:
      ip_address = requests.get('https://api.ipify.org?format=json').json()["ip"]
      city = requests.get(f"https://freeipapi.com/api/json/{ip_address}").json()["cityName"]

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_FETCH_API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        weather = data['weather'][0]['description']
        temperature = data['main']['temp']
        asyncio.run(speak(f"It's currently {weather} and {temperature}ºC in {city}."))
    else:
        print("Error:", data.get("message", "Could not retrieve weather data."))

def hotword():
  porcupine = None
  paud = None
  audio_stream = None
  access_key = "NDwgBowO/ci32IjnESusPj/SsNrZMniRRjc5zRSk4rpcrPJBnIhgag=="
  
  try:
    keyword_path = "www\\assets\\hey-aria_en_windows_v3_0_0.ppn"
    porcupine = pvporcupine.create(access_key=access_key, keyword_paths=[keyword_path])
    paud = pyaudio.PyAudio()
    audio_stream = paud.open(rate=porcupine.sample_rate, channels=1, format=pyaudio.paInt16, input=True, frames_per_buffer=porcupine.frame_length)

    while True:
      keyword = audio_stream.read(porcupine.frame_length)
      keyword = struct.unpack_from("h"*porcupine.frame_length, keyword)
      keyword_index = porcupine.process(keyword)

      if keyword_index >= 0:
        print("Hotword detected")
        import pyautogui as autogui
        autogui.keyDown("win")
        autogui.press("a")
        time.sleep(2)
        autogui.keyUp("win")
  except Exception as e:
    print(f"An error occurred: {e}")
  finally:
    # Ensure resources are released properly
    if porcupine is not None:
      porcupine.delete()
    if audio_stream is not None:
      audio_stream.close()
    if paud is not None:
      paud.terminate()

def find_contact(query):
  words_to_remove = [ASSISTANT_NAME, 'make', 'a', 'to', 'phone', 'call', 'send', 'message', 'whatsapp', 'video']
  query = remove_words(query, words_to_remove)

  try:
    query = query.strip().lower()
    cursor.execute("SELECT mobile_nr FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", ('%' + query + '%', query + '%'))
    results = cursor.fetchall()
    mobile_number_str = str(results[0][0])

    if not mobile_number_str.startswith('+34'):
      mobile_number_str = '+34' + mobile_number_str

    return mobile_number_str, query
  except:
    asyncio.run(speak("Contact doesn't exist"))
    return 0, 0
  
def whats_app(mobile_nr, message, flag, name):
  if flag == 'message':
    target_tab = 12
    aria_message = "Message send successfully to " + name
  elif flag == 'call':
    target_tab = 7
    message = ''
    aria_message = "Calling " + name
  else:
    target_tab = 6
    message = ''
    aria_message = "Starting video call with " + name

  encoded_message = quote(message)
  whatsapp_url = f"whatsapp://send?phone={mobile_nr}&text={encoded_message}"
  full_command = f'start "" "{whatsapp_url}"'

  subprocess.run(full_command, shell=True)
  time.sleep(5)
  subprocess.run(full_command, shell=True)

  pyautogui.hotkey('ctrl', 'f')

  for i in range(1, target_tab):
    pyautogui.hotkey('tab')

  pyautogui.hotkey('enter')
  asyncio.run(speak(aria_message))

def rate_limit_retry(func):
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry_error_callback=lambda retry_state: None
    )
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if "429" in str(e) or "Resource has been exhausted" in str(e):
                print(f"Rate limit hit, retrying after delay...")
                time.sleep(2)  # Add a small delay
                raise e  # Retry
            raise e
    return wrapper

@rate_limit_retry
def generate_with_backoff(prompt):
    return model.generate_content(prompt)

def chatbot(prompt):
    try:
        if prompt[:7].lower() == '/recall':
            prompt = prompt[8:]
            recall(prompt=prompt)
            response = stream_response(prompt=prompt)
        elif prompt[:7].lower() == '/forget':
            remove_last_conversation()
            return "Previous conversation removed."
        elif prompt[:9].lower() == '/memorize':
            prompt = prompt[10:]
            store_conversations(prompt=prompt, response='Memory stored.')
            return "Memory stored."
        else:
            response = stream_response(prompt=prompt)
            
        asyncio.run(speak(response))
        return response
    except Exception as e:
        print(f"Error in chatbot: {e}")
        return "I apologize, but I encountered an error processing your request."

def connect_db():
  conn = psycopg.connect(**DB_PARAMS)
  return conn

def fetch_conversations():
  conn = connect_db()
  with conn.cursor(row_factory=dict_row) as cursor:
    cursor.execute('SELECT * FROM conversations')
    conversations = cursor.fetchall()
  conn.close()
  return conversations

def store_conversations(prompt, response):
  conn = connect_db()
  with conn.cursor() as cursor:
    cursor.execute(
      'INSERT INTO conversations (timestamp, prompt, response) VALUES (CURRENT_TIMESTAMP, %s, %s)', (prompt, response)
    )
    conn.commit()
  conn.close()

def remove_last_conversation():
  conn = connect_db()
  with conn.cursor() as cursor:
    cursor.execute('DELETE FROM conversations WHERE id = (SELECT MAX(id) FROM conversations)')
    cursor.commit()
  conn.close()

def parse_generate_content_response(response):
    try:
        if hasattr(response, 'text'):
            return response.text
        # Fallback for different response types
        if hasattr(response, 'parts'):
            return response.parts[0].text
        return str(response)
    except Exception as e:
        print(f"Error while parsing response: {e}")
        return None

@rate_limit_retry
def stream_response(prompt):
    try:
        # Build the full conversation history
        messages = [{'role': 'system', 'content': system_prompt}]
        
        # Add previous conversations from memory
        try:
            conn = connect_db()
            with conn.cursor(row_factory=dict_row) as cursor:
                cursor.execute('SELECT prompt, response FROM conversations ORDER BY timestamp DESC LIMIT 10')
                prev_conversations = cursor.fetchall()
                
            # Add previous conversations in reverse order (oldest first)
            for conv in reversed(prev_conversations):
                messages.append({'role': 'user', 'content': conv['prompt']})
                messages.append({'role': 'assistant', 'content': conv['response']})
        except Exception as e:
            print(f"Error fetching conversation history: {e}")
        finally:
            conn.close()
            
        # Add the current prompt
        messages.append({'role': 'user', 'content': prompt})
        
        # Format the conversation into a single string
        conversation_text = "\n\nPrevious conversation:\n"
        for msg in messages:
            role = "Assistant" if msg['role'] == 'assistant' else "User" if msg['role'] == 'user' else "System"
            conversation_text += f"{role}: {msg['content']}\n"
        conversation_text += "\nCurrent prompt: " + prompt
        
        # Generate response with conversation context
        response = generate_with_backoff(conversation_text)
        
        if not response:
            return "I apologize, but I encountered an error processing your request."
            
        response_text = response.text if hasattr(response, 'text') else str(response)
        
        print('\nASSISTANT:')
        print(response_text)
        print('\n')
        
        if response_text:
            # Store the conversation
            store_conversations(prompt=prompt, response=response_text)
            return response_text
        else:
            return "I apologize, but I encountered an error processing your request."
    except Exception as e:
        print(f"Error in stream_response: {e}")
        return "I apologize, but I encountered an error processing your request."

def retrieve_embeddings(queries, results_per_query=5):
    embeddings = set()
    max_queries = min(len(queries), 3)  # Limit number of queries processed

    for query in tqdm(queries[:max_queries], desc='Processing queries to vector database'):
        try:
            # Use simple text matching instead of embeddings
            vector_db = client.get_collection(name='conversations')
            results = vector_db.query(
                query_texts=[query],
                n_results=results_per_query
            )
            
            if not results or 'documents' not in results or not results['documents']:
                continue
                
            best_embedding = results['documents'][0]

            for best in best_embedding:
                if best not in embeddings:
                    # Simple text similarity check instead of API call
                    if any(term.lower() in best.lower() for term in query.split()):
                        embeddings.add(best)
        except Exception as e:
            print(f"Error processing query '{query}': {e}")
            continue

    return embeddings

@rate_limit_retry
def create_queries(prompt):
    query_msg = (
        'You are a first principle reasoning search query AI agent. '
        'Create a Python list of up to 3 search queries to find relevant information. '
        'Keep queries short and focused. Response must be a valid Python list.'
    )

    try:
        response = generate_with_backoff(f"{query_msg}\n\nUser: {prompt}")
        if not response or not hasattr(response, 'text'):
            return [prompt]
            
        parsed_response = response.text
        print(f'\nVector database queries: {parsed_response} \n')

        try:
            queries = ast.literal_eval(parsed_response)
            return queries[:3]  # Limit to max 3 queries
        except:
            return [prompt]
    except Exception as e:
        print(f"Error creating queries: {e}")
        return [prompt]

def classify_embedding(query, context):
    classify_msg = (
        'You are an embedding classification AI agent. Your input will be a prompt and one embedded chunk of text. '
        'You will not respond as an AI assistant. You only respond "yes" or "no". '
        'Determine whether the context contains data that directly is related to the search query. '
        'If the context is seemingly exactly what the search query needs, respond "yes" if it is anything but directly '
        'related respond "no". Do not respond "yes" unless the content is highly relevant to the search query.'
    )

    try:
        message = f"{classify_msg}\n\nSEARCH QUERY: {query}\nEMBEDDED CONTEXT: {context}"
        response = model.generate_content(message)
        if not response or not hasattr(response, 'text'):
            return 'no'
            
        result = response.text.strip().lower()
        return 'yes' if result == 'yes' else 'no'
    except Exception as e:
        print(f"Error classifying embedding: {e}")
        return 'no'

def recall(prompt):
  queries = create_queries(prompt=prompt)
  embeddings = retrieve_embeddings(queries=queries)
  conversation.append({'role': 'user', 'content': f'MEMORIES: {embeddings} \n\n USER PROMPT: {prompt}'})
  print(f'\n{len(embeddings)} message: response embeddings added for context.')

def find_my_ip():
  ip_address = requests.get('https://api.ipify.org?format=json').json()
  asyncio.run(speak(f"Your IP address is {ip_address["ip"]}"))

def send_email(receiver, subject, message):
    try:
        email = EmailMessage()
        email["To"] = receiver
        email["Subject"] = subject
        email["From"] = EMAIL

        email.set_content(message)
        s = smtplib.SMTP(SMTP_URL, SMTP_PORT)
        s.starttls()
        s.login(EMAIL, PASSWORD)
        s.send_message(email)
        s.close()
        return True
    except Exception as e:
        print(e)
        return False

def get_news():
    news_headline = []
    result = requests.get(NEWS_FETCH_API_URL, params={"country": "us", "category": "general", "apiKey": NEWS_FETCH_API_KEY}).json()
    articles = result["articles"]
    for article in articles:
        news_headline.append(article["title"])

    asyncio.run(speak(f"The headlines of today are {news_headline[:6]}"))

def search_on_wikipedia(query):
  query = query.split("search", 1)[1].strip()
  query = query.replace("on wikipedia", "")
  print(query)
  results = wikipedia.summary(query, sentences=2)
  asyncio.run(speak(f"According to wikipedia, {results}"))

def search_on_google(query):
  query = query.split("search", 1)[1].strip()
  query = query.replace("on google", "")
  asyncio.run(speak(f"Searching {query} on Google"))
  kit.search(query)

def text_to_image(query):
    try:
      # Extract query and sanitize it for filename
      query = query.split("image", 1)[1].strip()
      sanitized_query = "".join(c if c.isalnum() or c in (" ", "_", "-") else "_" for c in query)

      print(f"Generating image for query: {query}")

      with autocast('cuda'):
        image = pipe(query).images[0]

      image_path = os.path.join("www", f"{sanitized_query}.png")
      image.save(image_path)

      asyncio.run(speak(f"Here is the image {query}"))
      eel.showImageCreated(f"{sanitized_query}.png")

    except Exception as e:
      print(f"An error occurred: {e}")
      asyncio.run(speak("Sorry, there was an error generating the image."))