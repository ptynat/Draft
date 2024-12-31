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
REPO_NAME = 'Ptynat_Draft'
BASE_URL = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/'

# List of valid players
players = ["Ezpzmaglll", "Silox", "Ptynat", "Saymus", "Secret"]

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
    data = {
        "message": "Updating JSON file",
        "content": content,
        "sha": sha
    }
    response = requests.put(url, headers=headers, data=json.dumps(data))
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
        counter_file = f'Counters/Counters_{player_name}.json'
        synergies_file = f'Synergies/Synergies_{player_name}.json'
        questionnaire_files = [counter_file, synergies_file]
        page_titles = ['Counters', 'Synergies']

        # Session state to track current questionnaire
        if 'current_questionnaire' not in st.session_state:
            st.session_state.current_questionnaire = 0

        if st.session_state.current_questionnaire < len(questionnaire_files):
            current_file = questionnaire_files[st.session_state.current_questionnaire]
            st.title(page_titles[st.session_state.current_questionnaire])

            try:
                file_content = get_file_content(current_file)
                if file_content:
                    decoded_content = json.loads(requests.get(file_content['download_url']).text)
                    st.header(f"Questionnaire {st.session_state.current_questionnaire + 1}")

                    # Display questionnaire
                    for hero, matchups in decoded_content.items():
                        st.subheader(f'For {hero}:')
                        for opponent in matchups.keys():
                            rating = st.slider(f'Rate {opponent}:', 0, 10, 5, key=f'{hero}_{opponent}')
                            decoded_content[hero][opponent] = rating

                    if st.button('Submit This Questionnaire'):
                        updated_content = json.dumps(decoded_content).encode('utf-8')
                        update_file_content(current_file, updated_content.decode('utf-8'), file_content['sha'])
                        st.session_state.current_questionnaire += 1
                        st.rerun()

            except Exception as e:
                st.error(f"No questionnaire found for {player_name} or error occurred: {e}")
        else:
            st.success("All questionnaires completed!")

