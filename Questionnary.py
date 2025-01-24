import streamlit as st
import json
import os
import requests

# Manually load environment variables from .env file (alternative method)
from pathlib import Path
#from dotenv import load_dotenv

env_path = Path('.') / '.env'
#load_dotenv(dotenv_path=env_path)

# GitHub configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = 'Ptynat'
REPO_NAME = 'Draft_Ptynat'
BASE_URL = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/'

# List of valid players
players = ["Ezpzmaglll", "Gerolly", "Ptynat", "Saymus", "Secret"]

# Function to get the file content from GitHub
def get_file_content(file_path):
    url = BASE_URL + file_path
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        content = response.json()
        return content
    else:
        st.error(f"Error fetching file: {response.status_code}")
        return None

# Function to update the file content on GitHub
def update_file_content(file_path, content, sha):
    url = BASE_URL + file_path
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    import base64
    encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    data = {
        "message": "Updating JSON file",
        "content": encoded_content,
        "sha": sha
    }
    response = requests.put(url, headers=headers, json=data)
    if response.status_code == 200:
        st.success("File updated successfully")
    else:
        st.error(f"Error updating file: {response.status_code}")

# Password protection
def check_password():
    """Returns `True` if the user had the correct password."""
    def password_entered():
        if st.session_state["password"] == os.getenv("PASSWORD"):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password
        st.text_input("Enter password:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Enter password:", type="password", on_change=password_entered, key="password")
        st.error("Password incorrect")
        return False
    else:
        return True
    
if check_password():
    # Player name input as a text field
    player_name = st.text_input("Enter your name:", "")
    
    # Validate if name exists in players list
    if player_name and player_name not in players:
        st.error("Player name not found. Please enter a valid name.")
        player_name = None

    if player_name:
        # Tabs for different questionnaires
        tab1, tab2, tab3 = st.tabs(["Counters", "Synergies", "Comfort"])
        
        with tab1:
            st.title("Counters Questionnaire")
            counter_file = f'data/Counters/Counters_{player_name}.json'
            file_content = get_file_content(counter_file)
            if file_content:
                decoded_content = json.loads(requests.get(file_content['download_url']).text)
                st.header("Rate from 0 (you counter them) to 10 (they counter you)")
                
                for hero, matchups in decoded_content.items():
                    with st.expander(f'Champion: {hero}'):
                        st.subheader(f'For {hero}:')
                        if st.button(f'Reset {hero} ratings', key=f'counter_reset_{hero}'):
                            for opponent in matchups.keys():
                                decoded_content[hero][opponent] = 5
                        for opponent in matchups.keys():
                            rating = st.slider(f'Rate {opponent}:', 0, 10, 
                                             decoded_content[hero][opponent], 
                                             key=f'counter_{hero}_{opponent}')
                            decoded_content[hero][opponent] = rating
                
                if st.button('Submit Counters'):
                    updated_content = json.dumps(decoded_content, indent=2)
                    update_file_content(counter_file, updated_content, file_content['sha'])
        
        with tab2:
            st.title("Synergies Questionnaire")
            synergies_file = f'data/Synergies/Synergies_{player_name}.json'
            file_content = get_file_content(synergies_file)
            if file_content:
                decoded_content = json.loads(requests.get(file_content['download_url']).text)
                st.header("Rate from 0 (no synergy) to 10 (high synergy)")
                
                for hero, matchups in decoded_content.items():
                    with st.expander(f'Champion: {hero}'):
                        st.subheader(f'For {hero}:')
                        for opponent in matchups.keys():
                            rating = st.slider(f'Rate {opponent}:', 0, 10, 
                                             decoded_content[hero][opponent], 
                                             key=f'synergy_{hero}_{opponent}')
                            decoded_content[hero][opponent] = rating
                
                if st.button('Submit Synergies'):
                    updated_content = json.dumps(decoded_content, indent=2)
                    update_file_content(synergies_file, updated_content, file_content['sha'])

        with tab3:
            st.title("Comfort Questionnaire")
            comfort_file = f'data/Comfort/Comfort_{player_name}.json'
            file_content = get_file_content(comfort_file)
            if file_content:
                decoded_content = json.loads(requests.get(file_content['download_url']).text)
                st.header("Rate from 0 (not comfortable) to 10 (very comfortable)")
                
                for hero, rating in decoded_content.items():
                    value = st.slider(f'Rate {hero}:', 0, 10, 
                                    rating,
                                    key=f'comfort_{hero}')
                    decoded_content[hero] = value
                
                if st.button('Submit Comfort'):
                    updated_content = json.dumps(decoded_content, indent=2)
                    update_file_content(comfort_file, updated_content, file_content['sha'])
