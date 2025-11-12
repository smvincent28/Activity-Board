import streamlit as st
import os

# Configure page
st.set_page_config(
    page_title="Family Fun Finder",
    page_icon="🎨",
    layout="wide"
)

# Try to import Gemini
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    st.error("⚠️ Installing required packages... Please wait and refresh the page in a moment.")

# Configure API if available
if GENAI_AVAILABLE:
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')
        else:
            st.error("⚠️ Please add GEMINI_API_KEY to Streamlit Secrets in Settings!")
            model = None
    except Exception as e:
        st.error(f"Error configuring API: {e}")
        model = None
else:
    model = None

# Initialize session state
if 'current_player' not in st.session_state:
    st.session_state.current_player = None
if 'players' not in st.session_state:
    st.session_state.players = {
        'Gabriel': {'points': 0, 'activities_completed': []},
        'Eliot': {'points': 0, 'activities_completed': []},
        'Levi': {'points': 0, 'activities_completed': []},
        'Olivia': {'points': 0, 'activities_completed': []}
    }
if 'screen' not in st.session_state:
    st.session_state.screen = 'welcome'
if 'current_activity' not in st.session_state:
    st.session_state.current_activity = None

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
    .points-display {
        font-size: 24px;
        font-weight: bold;
        color: #667eea;
        text-align: center;
    }
    div.stButton > button {
        width: 100%;
        height: 100px;
        font-size: 20px;
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
            st.markdown(f"### {avatar}")
            st.markdown(f"### {name}")
            if st.button(f"Pick Me!", key=f"player_{name}"):
                st.session_state.current_player = name
                st.session_state.screen = 'main_menu'
                st.rerun()
            st.caption(f"Points: {st.session_state.players[name]['points']}")

def main_menu():
    player = st.session_state.current_player
    
    st.markdown(f'<p class="big-font">Hey {player}! 👋</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="points-display">Your Points: {st.session_state.players[player]["points"]}</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🎲 Find Something Fun!", use_container_width=True):
            st.session_state.screen = 'activity_search'
            st.rerun()
    
    with col2:
        if st.button("📊 View Scoreboard", use_container_width=True):
            st.session_state.screen = 'scoreboard'
            st.rerun()
    
    with col3:
        if st.button("🏠 Back to Home", use_container_width=True):
            st.session_state.current_player = None
            st.session_state.screen = 'welcome'
            st.rerun()

def activity_search():
    player = st.session_state.current_player
    
    st.markdown(f"### What kind of activity are you looking for, {player}?")
    
    col1, col2 = st.columns(2)
    with col1:
        location = st.selectbox("Where do you want to play?", ["Indoor", "Outdoor", "Either"])
        duration = st.selectbox("How much time do you have?", 
                               ["Quick (5-15 min)", "Medium (15-30 min)", "Long (30-60 min)", "Any"])
    
    with col2:
        interests = st.multiselect("What are you interested in?", 
                                   ["building", "creative", "games", "art", "sports", "nature", "cooking"])
        
    bored_text = st.text_area("Tell me what you want to do:", 
                              placeholder="I'm bored! I want something fun to do!",
                              height=100)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.button("Find Activity!", type="primary", use_container_width=True):
            if not model:
                st.error("⚠️ AI is not configured yet. Please make sure google-generativeai is installed and API key is added!")
                return
                
            with st.spinner("Finding the perfect activity..."):
                prompt = f"""You are a fun and helpful guide for kids' activities.

The child's name is {player}, and they said: "{bored_text if bored_text else 'I want something fun to do!'}"

Preferences:
- Location: {location}
- Duration: {duration}
- Interests: {', '.join(interests) if interests else 'anything fun'}

Suggest ONE specific fun activity. Include:
1. Activity name (bold)
2. What they'll do (2-3 sentences)
3. Why it's perfect for them right now

Be enthusiastic! Keep it short and exciting!"""
                
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
                    st.error(f"Oops! Error getting activity: {e}")
    
    with col2:
        if st.button("Back", use_container_width=True):
            st.session_state.screen = 'main_menu'
            st.rerun()

def activity_reveal():
    player = st.session_state.current_player
    activity = st.session_state.current_activity
    
    st.markdown(f"### 🎉 Perfect Activity for {player}! 🎉")
    
    st.markdown("---")
    st.markdown(activity['suggestion'])
    st.markdown("---")
    
    st.info(f"**You can earn {activity['points']} points by completing this activity!**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("✅ I completed it!", type="primary", use_container_width=True):
            st.session_state.players[player]['points'] += activity['points']
            st.session_state.players[player]['activities_completed'].append({
                'activity': activity['suggestion'][:100],
                'points': activity['points']
            })
            st.success(f"Awesome! You earned {activity['points']} points! 🎊")
            st.balloons()
    
    with col2:
        if st.button("🔄 Show me something else", use_container_width=True):
            st.session_state.screen = 'activity_search'
            st.rerun()
    
    with col3:
        if st.button("🏠 Back to Menu", use_container_width=True):
            st.session_state.screen = 'main_menu'
            st.rerun()

def scoreboard():
    st.markdown('<p class="big-font">🏆 Scoreboard 🏆</p>', unsafe_allow_html=True)
    
    sorted_players = sorted(st.session_state.players.items(), 
                          key=lambda x: x[1]['points'], 
                          reverse=True)
    
    medals = ["🥇", "🥈", "🥉", "⭐"]
    
    for i, (name, data) in enumerate(sorted_players):
        medal = medals[i] if i < len(medals) else "🎯"
        
        col1, col2, col3 = st.columns([1, 3, 1])
        with col1:
            st.markdown(f"## {medal}")
        with col2:
            st.markdown(f"### {name}")
            st.caption(f"Activities completed: {len(data['activities_completed'])}")
        with col3:
            st.markdown(f"### {data['points']} pts")
        
        st.markdown("---")
    
    if st.button("Back to Menu", use_container_width=True):
        if st.session_state.current_player:
            st.session_state.screen = 'main_menu'
        else:
            st.session_state.screen = 'welcome'
        st.rerun()

# Main app
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
    if not GENAI_AVAILABLE:
        st.warning("⚠️ Waiting for packages to install. This may take a minute. Please refresh the page!")
    main()
