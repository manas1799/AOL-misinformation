import os
import json
import time
import praw
import pandas as pd
import numpy as np

# Reddit API credentials
CLIENT_ID = "WP-cpYYozBjZiUkX7qE9rQ"
CLIENT_SECRET = "ZmJQlQ-RkKXftFeDtZaE6K3PFvId0Q"
USER_AGENT = "AOL/misinformation-bot"

# Initialize the Reddit client
print("Initializing Reddit client...")
reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT
)
print("Reddit client initialized successfully.")

def fetch_comments(submission, comment_limit=50):
    """
    Fetches up to a specified number of comments for a given Reddit submission.

    Args:
        submission (praw.models.Submission): The Reddit submission.
        comment_limit (int): Maximum number of comments to fetch.

    Returns:
        list: A list of dictionaries containing comment details.
    """
    print(f"Fetching up to {comment_limit} comments for post ID: {submission.id}...")
    comments = []
    try:
        submission.comments.replace_more(limit=None)  # Fetch all comments
        all_comments = submission.comments.list()[:comment_limit]  # Limit the number of comments
        for comment in all_comments:
            comments.append({
                "body": comment.body,
                "author": str(comment.author),
                "score": comment.score,
                "created_utc": comment.created_utc,
            })
        print(f"Fetched {len(comments)} comments for post ID: {submission.id}.")
    except Exception as e:
        print(f"Error fetching comments for submission {submission.id}: {e}")
    return comments

def scrape_reddit_data(search_term, subreddit="all", limit=50, existing_ids=set()):
    """
    Scrapes Reddit posts and their comments based on a search term.

    Args:
        search_term (str): The search term to query.
        subreddit (str): The subreddit to search in. Default is "all".
        limit (int): The maximum number of posts to retrieve.
        existing_ids (set): Set of already processed post IDs.

    Returns:
        list: A list of dictionaries containing post and comment details.
    """
    print(f"Starting scrape for term '{search_term}' in subreddit '{subreddit}' with limit {limit}...")
    results = []
    try:
        for submission in reddit.subreddit(subreddit).search(search_term, limit=limit):
            if submission.id in existing_ids:
                print(f"Skipping duplicate post: {submission.title} (ID: {submission.id})")
                continue
            
            print(f"Processing post: {submission.title} (ID: {submission.id})")
            post_data = {
                "id": submission.id,  # Include post ID
                "title": submission.title,
                "content": submission.selftext,  # Add post content
                "url": submission.url,
                "score": submission.score,
                "num_comments": submission.num_comments,
                "created_utc": submission.created_utc,
                "subreddit": submission.subreddit.display_name,
                "author": str(submission.author),
                "comments": fetch_comments(submission)  # Fetch all comments
            }
            results.append(post_data)
            print(f"Post '{submission.title}' processed successfully.")
            # Save immediately after each post is processed
            save_to_file([post_data], filename, existing_ids)
    except Exception as e:
        print(f"An error occurred during scraping: {e}")
    print(f"Scrape completed. Total posts scraped: {len(results)}.")
    return results

def save_to_file(data, filename, existing_ids):
    """
    Saves data to a file in JSON format, ensuring no duplicates.

    Args:
        data (list): The data to save.
        filename (str): The name of the file to save the data to.
        existing_ids (set): Set of already saved post IDs, updated during the save process.
    """
    print(f"Saving data to file: {filename}...")
    try:
        with open(filename, "a", encoding="utf-8") as file:
            for item in data:
                if item["id"] not in existing_ids:
                    file.write(json.dumps(item, ensure_ascii=False) + "\n")
                    existing_ids.add(item["id"])  # Add ID to the set
        print(f"Data saved successfully to {filename}.")
    except Exception as e:
        print(f"Failed to save data: {e}")

def load_existing_ids(filename):
    """
    Loads existing post IDs from a file.

    Args:
        filename (str): The name of the file to read IDs from.

    Returns:
        set: A set of existing post IDs.
    """
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

if __name__ == "__main__":
    # Specify your search term and subreddit
    search_term = input("Please enter search term: ")
    subreddit = input("Enter a subreddit (or leave blank for 'all'): ") or "all"
    filename = input("Enter the filename to save data (e.g., data.json): ").strip()
    limit = 50  # Adjust the limit as per your needs

    # Load existing IDs
    existing_ids = load_existing_ids(filename)

    iteration_count = 0  # Counter for iterations
    max_iterations = 1   # Maximum iterations

    while iteration_count < max_iterations:
        try:
            print(f"\nIteration {iteration_count + 1}/{max_iterations}: Fetching data for term '{search_term}' in subreddit '{subreddit}'...")
            scrape_reddit_data(search_term, subreddit=subreddit, limit=limit, existing_ids=existing_ids)
            
            iteration_count += 1  # Increment the counter
            if iteration_count < max_iterations:
                print("Waiting for 60 seconds before the next fetch...")
                time.sleep(60)  # Wait 1 minute before retrying

        except Exception as e:
            print(f"An error occurred: {e}")
            print("Stopping the script.")
            break

    print("Script completed.")
