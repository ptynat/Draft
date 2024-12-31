import streamlit as st
import json
import os

# Use Streamlit secrets to access the password
PASSWORD = st.secrets["PASSWORD"]

# List of valid players
players = ["Ezpzmaglll", "Silox", "Ptynat", "Saymus", "Secret"]

# Password protection
def check_password():
    """Returns `True` if the user had the correct password."""
    def password_entered():
        if st.session_state["password"] == PASSWORD:
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
        # Create directories if they don't exist
        os.makedirs('Counters', exist_ok=True)
        os.makedirs('Synergies', exist_ok=True)

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
                with open(current_file, 'r') as file:
                    current_data = json.load(file)
                    st.header(f"Questionnaire {st.session_state.current_questionnaire + 1}")

                    # Display questionnaire
                    for hero, matchups in current_data.items():
                        st.subheader(f'For {hero}:')
                        for opponent in matchups.keys():
                            rating = st.slider(f'Rate {opponent}:', 0, 10, 5, key=f'{hero}_{opponent}')
                            current_data[hero][opponent] = rating

                    if st.button('Submit This Questionnaire'):
                        with open(current_file, 'w') as file:
                            json.dump(current_data, file)
                        st.session_state.current_questionnaire += 1
                        st.rerun()

            except FileNotFoundError:
                st.error(f"No questionnaire found for {player_name}")
        else:
            st.success("All questionnaires completed!")
