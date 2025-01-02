import os
import re
import time
import eel
import yt_dlp
import time
import pygame
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

def set_system_volume(volume_percentage):
    """
    Set the system volume on Windows, using percentage (0-100).
    
    :param volume_percentage: Integer between 0 and 100 representing the desired volume level.
    """
    # Ensure the volume percentage is between 0 and 100
    volume_percentage = min(max(volume_percentage, 0), 100)
    
    # Convert the percentage (0-100) to a scalar value (0.0 to 1.0)
    volume_level = volume_percentage / 100.0
    
    # Get the audio endpoint and volume interface
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    
    # Set the master volume level
    volume.SetMasterVolumeLevelScalar(volume_level, None)

def extract_yt_term(command):
  pattern = r'play\s(.*?)\s+on\s+youtube'
  match = re.search(pattern, command, re.IGNORECASE)

  return match.group(1) if match else None

def remove_words(input_string, words_to_remove):
  words = input_string.split()
  filtered_words = [word for word in words if word.lower() not in words_to_remove]
  result_string = ' '.join(filtered_words)

  return result_string

def download_and_play_youtube_audio(url):
    try:
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
            pygame.mixer.quit()
            eel.hideAudioControls()

        # Set up yt-dlp options to download audio
        ydl_opts = {
            'format': 'bestaudio/best',  # Download best audio format
            'outtmpl': 'youtube_audio',  # Output filename
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',  # Convert to MP3 format
                'preferredquality': '192',  # Set quality
            }],
            'noplaylist': True
        }

        # Download the audio using yt-dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(url)
            ydl.download([url])

        # The audio file name will be based on the output template
        audio_file = 'youtube_audio.mp3'  # Expected output file name

        # Initialize pygame mixer
        pygame.mixer.init()
        pygame.mixer.music.load(audio_file)  # Load the audio file

        # Play the audio
        print(f"Playing audio: {audio_file}")
        pygame.mixer.music.set_volume(0.5)
        eel.showAudioControls()
        pygame.mixer.music.play()

        audio_length = pygame.mixer.Sound(audio_file).get_length()

        # Wait until the audio is done playing
        while pygame.mixer.music.get_busy():
            # Get current playback position in seconds
            current_time = pygame.mixer.music.get_pos() / 1000  # Get position in milliseconds

            # Calculate the progress as a percentage
            progress = (current_time / audio_length) * 100

            # Update the frontend using Eel
            eel.updateAudioProgress(progress, current_time, audio_length)
            eel.sleep(1)  # Keep the UI responsive

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if pygame.mixer.get_init():
            pygame.mixer.quit()
            eel.hideAudioControls()
            
        # After stopping, delete the audio file
        if os.path.exists(audio_file):
            try:
                os.remove(audio_file)
                print(f"File {audio_file} has been deleted.")
            except Exception as delete_error:
                print(f"Failed to delete file: {delete_error}")

@eel.expose  # Expose this function to the JavaScript side
def stop_audio():
    # Stop the audio playback if it's still playing
    pygame.mixer.music.stop()  # Stop the music
    print("Music stopped.")

@eel.expose  # Expose this function to set the volume
def set_volume(volume):
    # Set the volume; volume should be a float between 0.0 and 1.0
    pygame.mixer.music.set_volume(volume)

def search_youtube(query):
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run headless if you don't want a browser window
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Create a new instance of the Chrome driver
    service = Service('C:\\Users\\mihai\\AppData\\Local\\Microsoft\\WindowsApps\\chromedriver-win64\\chromedriver.exe')  # Update this path to your ChromeDriver location
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Navigate to the YouTube search page
        driver.get(f"https://www.youtube.com/results?search_query={query}")
        
        # Wait for the page to load
        time.sleep(2)  # You can adjust this based on your connection speed

        # Find the first video link
        video_elements = driver.find_elements(By.XPATH, "//a[@href and contains(@href, '/watch?v=')]")
        if video_elements:
            video_link = f"{video_elements[0].get_attribute('href')}"
            return video_link
        else:
            return "No video link found."
    finally:
        # Close the browser
        driver.quit()