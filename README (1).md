# Family Fun Finder 🎨

A fun activity suggestion app for Gabriel, Eliot, Levi, and Olivia!

## Features
- Personalized activity suggestions using AI
- Point tracking system
- Scoreboard to see who's completed the most activities
- Multiple activity categories: LEGO, Outdoor Games, Seasonal activities, and more!

## Deploy to Streamlit Cloud (FREE!)

### Step 1: Upload to GitHub
1. Go to your GitHub account
2. Create a new repository called "family-fun-finder-app"
3. Upload these files:
   - `family_fun_finder.py`
   - `requirements.txt`
   - `README.md`

### Step 2: Deploy on Streamlit
1. Go to https://streamlit.io/cloud
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository: "family-fun-finder-app"
5. Main file path: `family_fun_finder.py`
6. Click "Deploy"!

### Step 3: Add your API Key
1. In Streamlit Cloud, click on your app settings (⚙️)
2. Go to "Secrets"
3. Add this:
   ```
   GEMINI_API_KEY = "your-api-key-here"
   ```
4. Save!

## Your app will be live at: your-app-name.streamlit.app

Share this link with your kids and they can use it anytime! 🎉

## Data Persistence
Points and completed activities are saved during each session. To make data permanent across sessions, we can add a simple database (let me know if you want this feature!).
