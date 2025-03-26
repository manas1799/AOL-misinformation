
import streamlit as st
import praw
import requests
from datetime import datetime
from streamlit.runtime.scriptrunner import get_script_run_ctx
from afinn import Afinn
from functools import lru_cache

# Page Config
st.set_page_config(page_title="Opportunities on Reddit", layout="wide")
st.title("🚀 Opportunities on Reddit")

# Reddit API Credentials
REDDIT_CLIENT_ID = "is5usa5dbOi9zkcqB2Zl7A"
REDDIT_CLIENT_SECRET = "yXgoahsClyIX7rRDRoo1SXY3UnFiMw"
REDDIT_USER_AGENT = "aol/1.0 by u/GullibleCarpet9254"

# Together AI API
API_KEY = "016db26241d4d9b200f03d6deccaf23ccc487ce57b8072a2b8de9d002791c0ee"
API_URL = "https://api.together.xyz/v1/chat/completions"

reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT,
)

SEARCH_TERMS = ["sleep", "anxiety", "hypertension", "stress", "insomnia", "night tremors"]


# 🔄 Cache refresh daily at 6 AM
@st.cache_data(ttl=24 * 60 * 60, show_spinner=True)
def fetch_and_filter_posts():
    opportunity_posts = []
    for term in SEARCH_TERMS:
        results = reddit.subreddit("all").search(term, sort="relevance", limit=15)
        for post in results:
            content = post.title + "\n\n" + post.selftext[:500]
            if is_help_needed(content):
                opportunity_posts.append({
                    "url": post.url,
                    "title": post.title,
                    "selftext": post.selftext[:300]
                })
    return opportunity_posts

# 🔍 Llama check if help is needed
def is_help_needed(post_content):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
        "messages": [{"role": "user", "content": f"Read the following Reddit post and answer ONLY 'yes' if the post shows the person is seeking help or needs help. Else answer 'no'.\n{post_content}"}]
    }
    try:
        response = requests.post(API_URL, headers=headers, json=data)
        answer = response.json()['choices'][0]['message']['content'].strip().lower()
        return "yes" in answer
    except Exception as e:
        st.error(f"AI check failed: {e}")
        return False

# 🔁 Optional Auto-refresh logic if running on a schedule (You can also use Streamlit Community Cloud scheduled runs)
current_time = datetime.now()
if current_time.hour == 6 and current_time.minute < 5:
    st.cache_data.clear()

st.info("Fetching and filtering Reddit posts... Please wait ⏳")
opportunity_posts = fetch_and_filter_posts()

if opportunity_posts:
    st.success(f"✅ Found {len(opportunity_posts)} opportunity posts where users seem to need help.")
    for post in opportunity_posts:
        st.markdown(f"""
            <div style='font-size: 16px; line-height: 1.5;'>
                <strong>Title:</strong> {post['title']}<br>
                <strong>Excerpt:</strong> {post['selftext']}<br>
                <a href="{post['url']}" target="_blank">🔗 View Post</a>
            </div>
            <hr style='border: 1px solid #444;'/>
        """, unsafe_allow_html=True)
else:
    st.warning("No opportunities found right now. Check back tomorrow!")

