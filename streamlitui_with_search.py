import streamlit as st
from textblob import TextBlob
import praw  # Reddit API Wrapper
import openai  # AI-Powered Response Generation
from afinn import Afinn


st.set_page_config(layout="wide")

afinn = Afinn()
# Reddit API Credentials (Replace with your own credentials)
REDDIT_CLIENT_ID = "is5usa5dbOi9zkcqB2Zl7A"
REDDIT_CLIENT_SECRET = "yXgoahsClyIX7rRDRoo1SXY3UnFiMw"
REDDIT_USER_AGENT = "aol/1.0 by u/GullibleCarpet9254"

OPENAI_API_KEY = "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"

import requests

API_KEY = "016db26241d4d9b200f03d6deccaf23ccc487ce57b8072a2b8de9d002791c0ee"  # Replace with your actual API key

API_URL = "https://api.together.xyz/v1/chat/completions"

# Authenticate Reddit API
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT,
)

# Fetch Top 10 Posts from a Subreddit
def fetch_reddit_posts_by_subreddit(subreddit="Art of Living"):
    posts = {}
    for post in reddit.subreddit(subreddit).hot(limit=10):  # Get 10 hot posts
        posts[post.url] = post.title + "\n\n" + post.selftext[:500]  # Longer text preview
    return posts

def fetch_reddit_posts(search_term = "Art of Living"):
    # Search Reddit across all subreddits
    results = reddit.subreddit("all").search(search_term, sort="relevance", limit=10)
    
    posts = {}
    # Print the top 10 search results
    for index, post in enumerate(results, start=1):
        posts[post.url] = post.title + "\n\n" + post.selftext[:500]

    return posts

# Generate AI-Powered Response using OpenAI API
def generate_ai_response(post_content):

    headers = {
        "Authorization": f"Bearer {API_KEY}",  # Add API key
        "Content-Type": "application/json"
    }

    data = {
        "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo",  # Or "meta-llama/Llama-3-8B-Instruct"
        "messages": [{"role": "user", "content": f"Generate a short response for the following Reddit post in support of art of living :\n{post_content}"}]
    }

    response = requests.post(API_URL, headers=headers, json=data)

    return response.json()['choices'][0]['message']['content']

def get_sentiment(post_content):

    headers = {
        "Authorization": f"Bearer {API_KEY}",  # Add API key
        "Content-Type": "application/json"
    }

    data = {
        "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo",  # Or "meta-llama/Llama-3-8B-Instruct"
        "messages": [{"role": "user", "content": f"Does the following content speak in support of Art of Living or against. Answer only supports, neutral or against \n{post_content}"}]
    }

    response = requests.post(API_URL, headers=headers, json=data)

    return response.json()['choices'][0]['message']['content']



# Custom CSS to increase the width of the first column (Reddit list)
st.markdown(
    """
    <style>
    div[data-testid="column"]:nth-of-type(1) {
        flex: 1.8;  /* Make left panel wider */
    }
    div[data-testid="column"]:nth-of-type(2),
    div[data-testid="column"]:nth-of-type(3) {
        flex: 1;  /* Keep other panels normal */
    }
    /* Custom styling for colored posts */
    .positive { background-color: #4CAF50; color: white; padding: 10px; border-radius: 5px; margin-bottom: 5px; }
    .neutral { background-color: #FFA500; color: white; padding: 10px; border-radius: 5px; margin-bottom: 5px; }
    .negative { background-color: #FF5733; color: white; padding: 10px; border-radius: 5px; margin-bottom: 5px; }
    </style>
    """,
    unsafe_allow_html=True
)


if st.button("Get Opportunity 🚀"):
    st.switch_page("pages/opportunity.py")

reddit_posts ={}

# Function to analyze sentiment and assign colors
def get_sentiment_class(text):
    #sentiment_score = TextBlob(text).sentiment.polarity
    sentiment_score = afinn.score(title) #st.session_state.sentiment_scores[url]  #
    print(f"Sentiment Score: {sentiment_score}")
    if sentiment_score >= 2:
        return "positive"  # Green for positive sentiment
    elif sentiment_score <= -0.2:
        return "negative"  # Red for negative sentiment
    else:
        return "neutral"  # Orange for neutral sentiment

# Search Bar (Top of Page)
st.title("🔍 Search & Explore Reddit Posts by Sentiment")
search_query = st.text_input("Enter a keyword to filter posts:", "")

# Load Reddit Posts
reddit_posts = fetch_reddit_posts(search_query)  # Change subreddit as needed
reddit_posts["https://www.reddit.com/r/technology/post1"] = "Art of Living was a life changing experience for me ! i recommend everyone to do this"

# Filter Reddit posts based on search query
#filtered_posts = {url: title for url, title in reddit_posts.items() if search_query.lower() in title.lower()}

# Create layout with three columns (List on left, Post in middle, Response on right)
col1, col2, col3 = st.columns([4, 3, 3])

# ✅ Initialize Sentiment Analysis in Session State (First Run Only)
if "sentiment_scores" not in st.session_state:
    st.session_state.sentiment_scores = {
        url: afinn.score(title) for url, title in reddit_posts.items()
    }


# Left Column: Clickable Reddit URLs (Wider panel)
with col1:
    st.subheader("📌 Click a Reddit Post (Color Coded by Sentiment):")
    if not reddit_posts:
        st.write("No results found for your search.")

    for url, title in reddit_posts.items():
        # Positive score = positive sentiment
        sentiment_class = get_sentiment_class(title) #get_sentiment_class(title)
 
        
        styled_block = f"""
            <div class="{sentiment_class}" style="cursor: pointer; padding: 10px; margin: 5px 0; 
            border-radius: 5px; font-weight: bold;" onclick="window.open('{url}', '_blank')">
                {title[:50]}... <br>
            </div>
        """
        st.markdown(styled_block, unsafe_allow_html=True)


        if st.button(url, key=url):  # Button contains title + URL
            st.session_state.selected_post = url
            st.session_state.generated_response = None  # Reset response

# Middle Column: Display Reddit Post Content
with col2:
    st.markdown('<div class="stSidebar">', unsafe_allow_html=True)
    st.subheader("📄 Reddit Post Content")

    if "selected_post" in st.session_state:
        selected_url = st.session_state.selected_post
        selected_text = reddit_posts.get(selected_url, "Post content not available.")

        st.markdown(f'<div class="selected-content">{selected_text}</div>', unsafe_allow_html=True)

        # Generate AI Response Button
        if st.button("📝 Generate AI Response"):
            ai_generated_response = generate_ai_response(selected_text)
            st.session_state.generated_response = ai_generated_response #f"AI-generated response for: {selected_text}"

    else:
        st.write("Click on a Reddit post to see details here.")

    st.markdown('</div>', unsafe_allow_html=True)

# Right Column: Generated AI Response (Appears when "Generate Response" is clicked)
with col3:
    if "generated_response" in st.session_state and st.session_state.generated_response:
        st.markdown('<div class="stSidebar">', unsafe_allow_html=True)
        st.subheader("🤖 AI-Powered Response")

        # Grey background for response
        st.markdown(
            f"""
            <div class="copy-button">
                <p>{st.session_state.generated_response}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Copy to clipboard button
        if st.button("📋 Copy Response"):
            st.session_state.copied_response = st.session_state.generated_response
            st.success("Response copied to clipboard!")

        st.markdown('</div>', unsafe_allow_html=True)
