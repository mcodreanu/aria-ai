import asyncio
import inspect
import re
import edge_tts
import os
import pygame
import speech_recognition as sr
import eel
import time
from importlib import import_module

async def speak(text):
    try:
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
            pygame.mixer.quit()
            eel.hideAudioControls()

        text = str(text)
        tts = edge_tts.Communicate(text, voice='en-US-JennyNeural')
        temp_audio_file = "temp_audio.mp3"
        
        await tts.save(temp_audio_file)
        
        eel.DisplayMessage(text)
        eel.receiverText(text)

        pygame.mixer.init()
        pygame.mixer.music.load(temp_audio_file)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            await asyncio.sleep(1)
    except Exception as e:
        print(f"Error during speech synthesis: {e}")
    finally:
        if pygame.mixer.get_init():
            pygame.mixer.quit()

        if os.path.exists(temp_audio_file):
            os.remove(temp_audio_file)

@eel.expose
def take_command():
    r = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            print('Adjusting for ambient noise...')
            r.adjust_for_ambient_noise(source, duration=1) 

            print('Listening...')
            eel.DisplayMessage('Listening...')
            r.pause_threshold = 1

            audio = r.listen(source, timeout=10, phrase_time_limit=6) 

        print('Recognizing...')
        eel.DisplayMessage('Recognizing...')
        query = r.recognize_google(audio, language='en-US')

        print(f"User said: {query}")
        time.sleep(1)

        return query.lower()

    except sr.WaitTimeoutError:
        print("Listening timed out while waiting for phrase.")
        eel.DisplayMessage("Listening timed out. Please try again.")
        return ""

    except sr.UnknownValueError:
        print("Could not understand the audio.")
        eel.DisplayMessage("Sorry, I couldn't understand that. Could you repeat?")
        return ""

    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        eel.DisplayMessage("Error contacting the recognition service. Please try again later.")
        return ""

    except Exception as e:
        print(f"An error occurred: {e}")
        eel.DisplayMessage(f"An unexpected error occurred: {e}")
        return ""

@eel.expose
def all_commands(message = 1):
    query = take_command() if message == 1 else message
    eel.senderText(query)

    if "stop" in query:
        if pygame.mixer.get_init():
            pygame.mixer.stop()
            pygame.mixer.quit()
            eel.hideAudioControls()
            print("Stopping.")
        return
    elif "exit" in query:
        from engine.features import chatbot
        asyncio.run(speak("Goodbye, Alex"))
        os.system('taskkill /F /IM msedge.exe')
        exit()

    try:
        command_patterns = {
            r"\bopen\b": "open_command",
            r"\bon youtube\b": "play_youtube",
            r"\bplay\b": "play_music",
            r"\bweather\b": "get_weather",
            r"\bip address\b": "find_my_ip",
            r"\bon google\b": "search_on_google",
            r"\bon wikipedia\b": "search_on_wikipedia",
            r"(create|generate|make) image": "text_to_image",
            r"(current|what's the) time": "get_time",
            r"\bset volume\b": "set_volume",
            r"\bspeed test\b": "get_internet_speed",
            r"\btell me the latest news\b": "get_news",
        }

        for pattern, func_name in command_patterns.items():
            if re.search(pattern, query):
                module = import_module('engine.features')
                command_func = getattr(module, func_name)

                # Check the number of parameters the function expects
                num_params = len(inspect.signature(command_func).parameters)

                # Call the function with or without the query parameter based on its signature
                if num_params == 1:
                    command_func(query)
                else:
                    command_func()
                return

        if re.search(r"(send message|phone call|video call)", query):
            from engine.features import find_contact, whats_app
            contact_nr, name = find_contact(query)
            if contact_nr != 0:
                flag = ""
                if "send message" in query:
                    flag = 'message'
                    asyncio.run(speak("What message should I send?"))
                    query = take_command()
                elif "phone call" in query:
                    flag = 'call'
                else:
                    flag = 'video call'

                whats_app(contact_nr, query, flag, name)
            return

        if re.search(r"(send email)", query):
            from engine.features import send_email
            asyncio.run(speak("To whom do you want to send the email?. Please enter in the terminal"))
            receiver_add = take_command()
            asyncio.run(speak("What is the subject?"))
            subject = take_command().capitalize()
            asyncio.run(speak("And what is the message you want to send?"))
            message = take_command().capitalize()
            if send_email(receiver_add, subject, message):
                asyncio.run(speak("I have sent the email sir"))
                print("I have sent the email sir")
            else:
                asyncio.run(speak("Something went wrong! Please check the error log"))
            return
        
        from engine.features import chatbot
        chatbot(query)
    except Exception as e:
        print(f"Error processing command: {e}") 

    eel.ShowMainPage()


