import os
import json
import time
import praw
import random

# Reddit API credentials
CLIENT_ID = "WP-cpYYozBjZiUkX7qE9rQ"
CLIENT_SECRET = "ZmJQlQ-RkKXftFeDtZaE6K3PFvId0Q"
USER_AGENT = "AOL/misinformation-bot"

# List of search terms
SEARCH_TERMS = ["Art of Living", "Meditation", "sleep", "insomnia", "Spirituality", "sri sri ravi shankar", "sudarshan kriya", "sri sri", "bangalore ashram", "silence course"]

# Initialize Reddit client
print("Initializing Reddit client...")
reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT
)
print("Reddit client initialized successfully.")

def fetch_comments(submission, comment_limit=20):
    """Fetches top comments for a given Reddit submission with rate-limiting handling."""
    print(f"Fetching top {comment_limit} comments for post ID: {submission.id}...")
    comments = []
    try:
        submission.comment_sort = "top"
        submission.comments.replace_more(limit=0)
        all_comments = submission.comments.list()[:comment_limit]

        for comment in all_comments:
            comments.append({
                "body": comment.body,
                "author": str(comment.author),
                "score": comment.score,
                "created_utc": comment.created_utc,
            })
            time.sleep(random.uniform(1, 3))  # Random delay (1-3 sec) between comment fetches

        print(f"Fetched {len(comments)} comments for post ID: {submission.id}.")
    except Exception as e:
        print(f"Error fetching comments for submission {submission.id}: {e}")
    return comments

def scrape_reddit_data(search_term, subreddit="all", limit=50, existing_ids=set(), filename="output.json"):
    """Scrapes Reddit posts from the last 4 months while handling rate limits."""
    print(f"Starting scrape for term '{search_term}' in subreddit '{subreddit}' with limit {limit}...")
    results = []
    four_months_ago = time.time() - (120 * 24 * 60 * 60)  # Timestamp for 4 months ago

    try:
        for submission in reddit.subreddit(subreddit).search(search_term, limit=limit, sort="new"):
            if submission.id in existing_ids:
                print(f"Skipping duplicate post: {submission.title} (ID: {submission.id})")
                continue

            if submission.created_utc < four_months_ago:
                print(f"Skipping old post: {submission.title} (ID: {submission.id}) - Older than 4 months")
                continue

            print(f"Processing post: {submission.title} (ID: {submission.id})")
            post_data = {
                "id": submission.id,
                "title": submission.title,
                "url": submission.url,
                "score": submission.score,  # Likes count
                "created_utc": submission.created_utc,
                "subreddit": submission.subreddit.display_name,
                "author": str(submission.author),
                "comments": fetch_comments(submission, comment_limit=20)
            }
            results.append(post_data)
            print(f"Post '{submission.title}' processed successfully.")
            save_to_file([post_data], filename, existing_ids)

            time.sleep(random.uniform(2, 5))  # Random delay (2-5 sec) between posts to avoid rate limits

    except Exception as e:
        print(f"An error occurred during scraping: {e}")
    print(f"Scrape completed. Total posts scraped: {len(results)}.")
    return results

def save_to_file(data, filename, existing_ids):
    """Saves data to a JSON file, avoiding duplicates."""
    print(f"Saving data to file: {filename}...")
    try:
        with open(filename, "a", encoding="utf-8") as file:
            for item in data:
                if item["id"] not in existing_ids:
                    file.write(json.dumps(item, ensure_ascii=False) + "\n")
                    existing_ids.add(item["id"])
        print(f"Data saved successfully to {filename}.")
    except Exception as e:
        print(f"Failed to save data: {e}")

def load_existing_ids(filename):
    """Loads existing post IDs from a file."""
    existing_ids = set()
    if os.path.exists(filename):
        print(f"Loading existing post IDs from {filename}...")
        with open(filename, "r", encoding="utf-8") as file:
            for line in file:
                try:
                    post = json.loads(line)
                    existing_ids.add(post["id"])
                except json.JSONDecodeError:
                    print("Skipping a malformed line in the file.")
    return existing_ids

def format_filename(search_term):
    """Converts search term to a valid filename format."""
    return search_term.lower().replace(" ", "_") + ".json"

if __name__ == "__main__":
    subreddit = "all"  # Change this if you want to search in a specific subreddit
    limit = 50  # Number of posts per search term

    for term in SEARCH_TERMS:
        filename = format_filename(term)  # Convert search term to file-friendly format
        print(f"\n--- Running search for: '{term}' ---")
        existing_ids = load_existing_ids(filename)  # Load existing post IDs

        scrape_reddit_data(term, subreddit=subreddit, limit=limit, existing_ids=existing_ids, filename=filename)

        wait_time = random.uniform(60, 180)  # Random wait time between 1-3 minutes before next search
        print(f"\nWaiting for {int(wait_time)} seconds before the next search...")
        time.sleep(wait_time)

    print("\nAll search terms completed successfully!")
