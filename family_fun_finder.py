import streamlit as st
import google.generativeai as genai
import json
import os
from datetime import datetime

# Configure page
st.set_page_config(
    page_title="Family Fun Finder",
    page_icon="🎨",
    layout="wide"
)

# Configure Gemini API
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

# Initialize session state
if 'current_player' not in st.session_state:
    st.session_state.current_player = None
if 'players' not in st.session_state:
    st.session_state.players = {
        'Gabriel': {'points': 0, 'activities_completed': [], 'interests': []},
        'Eliot': {'points': 0, 'activities_completed': [], 'interests': []},
        'Levi': {'points': 0, 'activities_completed': [], 'interests': []},
        'Olivia': {'points': 0, 'activities_completed': [], 'interests': []}
    }
if 'screen' not in st.session_state:
    st.session_state.screen = 'welcome'
if 'current_activity' not in st.session_state:
    st.session_state.current_activity = None

# Activity database (sample - you can expand this)
ACTIVITIES = [
    {
        "id": 101,
        "name": "LEGO Tower Challenge",
        "description": "Build the tallest tower you can without it falling!",
        "category": "lego",
        "duration": "quick",
        "location": "indoor",
        "points": 15,
        "age_min": 3,
        "age_max": 13,
        "interests": ["building", "creative", "challenge"]
    },
    {
        "id": 201,
        "name": "Paper Snowflake Decorations",
        "description": "Create beautiful snowflakes to hang around the house!",
        "category": "creative",
        "duration": "medium",
        "location": "indoor",
        "points": 25,
        "age_min": 5,
        "age_max": 13,
        "interests": ["art", "creative", "decorating"]
    },
    {
        "id": 601,
        "name": "Capture the Flag",
        "description": "Play the classic outdoor team game!",
        "category": "games",
        "duration": "long",
        "location": "outdoor",
        "points": 35,
        "age_min": 7,
        "age_max": 13,
        "interests": ["games", "team", "running", "strategy"]
    }
]

# Custom CSS
st.markdown("""
<style>
    .big-font {
        font-size: 50px !important;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 20px;
    }
    .player-card {
        padding: 20px;
        border-radius: 15px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        text-align: center;
        margin: 10px;
        cursor: pointer;
        transition: transform 0.2s;
    }
    .player-card:hover {
        transform: scale(1.05);
    }
    .activity-card {
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #e0e0e0;
        margin: 10px 0;
    }
    .points-display {
        font-size: 24px;
        font-weight: bold;
        color: #667eea;
    }
</style>
""", unsafe_allow_html=True)

def welcome_screen():
    st.markdown('<p class="big-font">🎨 Family Fun Finder 🎉</p>', unsafe_allow_html=True)
    st.markdown("### Welcome! Who's ready for some fun?")
    
    cols = st.columns(4)
    avatars = ["🦁", "🐼", "🦄", "🐉"]
    names = ["Gabriel", "Eliot", "Levi", "Olivia"]
    
    for i, (col, name, avatar) in enumerate(zip(cols, names, avatars)):
        with col:
            if st.button(f"{avatar}\n{name}", key=f"player_{name}", use_container_width=True):
                st.session_state.current_player = name
                st.session_state.screen = 'main_menu'
                st.rerun()
            st.caption(f"Points: {st.session_state.players[name]['points']}")

def main_menu():
    player = st.session_state.current_player
    
    st.markdown(f'<p class="big-font">Hey {player}! 👋</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="points-display">Your Points: {st.session_state.players[player]["points"]}</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🎲 Find Something Fun!", use_container_width=True, key="find_activity"):
            st.session_state.screen = 'activity_search'
            st.rerun()
    
    with col2:
        if st.button("📊 View Scoreboard", use_container_width=True, key="scoreboard"):
            st.session_state.screen = 'scoreboard'
            st.rerun()
    
    with col3:
        if st.button("🏠 Back to Home", use_container_width=True, key="back_home"):
            st.session_state.current_player = None
            st.session_state.screen = 'welcome'
            st.rerun()

def activity_search():
    player = st.session_state.current_player
    
    st.markdown(f"### What kind of activity are you looking for, {player}?")
    
    # User inputs
    col1, col2 = st.columns(2)
    with col1:
        location = st.selectbox("Where do you want to play?", ["Indoor", "Outdoor", "Either"])
        duration = st.selectbox("How much time do you have?", ["Quick (5-15 min)", "Medium (15-30 min)", "Long (30-60 min)", "Epic (1+ hours)", "Any"])
    
    with col2:
        interests = st.multiselect("What are you interested in?", 
                                   ["building", "creative", "games", "art", "sports", "nature", "cooking", "music"])
        age = st.slider("Age", 3, 13, 8)
    
    bored_text = st.text_input("Tell me how you're feeling or what you want to do:", placeholder="I'm bored! Give me something fun!")
    
    if st.button("Find Activity!", type="primary"):
        with st.spinner("Finding the perfect activity..."):
            # Generate activity suggestion using AI
            prompt = f"""You are a fun and helpful guide for kids' activities.
            
            The child's name is {player}, and they are looking for something to do.
            They said: "{bored_text}"
            
            Preferences:
            - Location: {location}
            - Duration: {duration}
            - Interests: {', '.join(interests) if interests else 'anything fun'}
            - Age: {age}
            
            Based on this, suggest ONE specific activity from the following categories:
            LEGO challenges, Christmas activities, Thanksgiving activities, Spring activities, 
            Fall activities, or Outdoor games.
            
            Provide:
            1. Activity name
            2. Brief description (1-2 sentences)
            3. Why it's perfect for them right now
            
            Be enthusiastic and encouraging! Keep it short and exciting."""
            
            try:
                response = model.generate_content(prompt)
                suggestion = response.text
                
                st.session_state.current_activity = {
                    'suggestion': suggestion,
                    'points': 25
                }
                st.session_state.screen = 'activity_reveal'
                st.rerun()
            except Exception as e:
                st.error(f"Oops! Something went wrong: {e}")
    
    if st.button("Back", key="back_from_search"):
        st.session_state.screen = 'main_menu'
        st.rerun()

def activity_reveal():
    player = st.session_state.current_player
    activity = st.session_state.current_activity
    
    st.markdown(f"### Perfect Activity for {player}! 🎉")
    
    st.markdown(f"""
    <div class="activity-card">
    {activity['suggestion']}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"**You can earn {activity['points']} points by completing this activity!**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("✅ I completed it!", type="primary"):
            st.session_state.players[player]['points'] += activity['points']
            st.session_state.players[player]['activities_completed'].append(activity['suggestion'][:50])
            st.success(f"Awesome! You earned {activity['points']} points! 🎊")
            st.balloons()
    
    with col2:
        if st.button("🔄 Show me something else"):
            st.session_state.screen = 'activity_search'
            st.rerun()
    
    with col3:
        if st.button("🏠 Back to Menu"):
            st.session_state.screen = 'main_menu'
            st.rerun()

def scoreboard():
    st.markdown('<p class="big-font">🏆 Scoreboard 🏆</p>', unsafe_allow_html=True)
    
    # Sort players by points
    sorted_players = sorted(st.session_state.players.items(), 
                          key=lambda x: x[1]['points'], 
                          reverse=True)
    
    medals = ["🥇", "🥈", "🥉", "⭐"]
    
    for i, (name, data) in enumerate(sorted_players):
        medal = medals[i] if i < len(medals) else "🎯"
        
        with st.container():
            col1, col2, col3 = st.columns([1, 3, 1])
            with col1:
                st.markdown(f"## {medal}")
            with col2:
                st.markdown(f"### {name}")
                st.markdown(f"Activities completed: {len(data['activities_completed'])}")
            with col3:
                st.markdown(f"### {data['points']} pts")
            
            st.divider()
    
    if st.button("Back to Menu"):
        st.session_state.screen = 'main_menu'
        st.rerun()

# Main app logic
def main():
    if st.session_state.screen == 'welcome':
        welcome_screen()
    elif st.session_state.screen == 'main_menu':
        main_menu()
    elif st.session_state.screen == 'activity_search':
        activity_search()
    elif st.session_state.screen == 'activity_reveal':
        activity_reveal()
    elif st.session_state.screen == 'scoreboard':
        scoreboard()

if __name__ == "__main__":
    main()
