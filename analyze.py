import os
import csv
import time
import datetime
from persistent_twitter import PersistentTwitter

def analyze_engagement(twitter, look_back=20):
    """
    Analyze a user's tweets and collect engagement data
    
    Args:
        twitter: PersistentTwitter instance
        look_back: Number of tweets to analyze
        
    Returns:
        Dictionary of engagement data
    """
    print(f"Analyzing the last {look_back} tweets for engagement...")
    
    # Get the user's tweets
    tweets = twitter.get_profile_tweets(count=look_back)
    print(f"Found {len(tweets)} tweets to analyze")
    
    # Dictionary to store engagement counts
    engagement_data = {}
    
    # Process each tweet
    for i, tweet in enumerate(tweets):
        print(f"Processing tweet {i+1}/{len(tweets)}: {tweet['url']}")
        
        # Get engagement data for this tweet
        engagements = twitter.get_tweet_engagements(tweet['url'])
        
        # Update the engagement data
        for username in engagements['likes']:
            if username not in engagement_data:
                engagement_data[username] = {'likes': 0, 'replies': 0, 'retweets': 0, 'quotes': 0}
            engagement_data[username]['likes'] += 1
            
        for username in engagements['replies']:
            if username not in engagement_data:
                engagement_data[username] = {'likes': 0, 'replies': 0, 'retweets': 0, 'quotes': 0}
            engagement_data[username]['replies'] += 1
            
        for username in engagements['retweets']:
            if username not in engagement_data:
                engagement_data[username] = {'likes': 0, 'replies': 0, 'retweets': 0, 'quotes': 0}
            engagement_data[username]['retweets'] += 1
            
        for username in engagements['quotes']:
            if username not in engagement_data:
                engagement_data[username] = {'likes': 0, 'replies': 0, 'retweets': 0, 'quotes': 0}
            engagement_data[username]['quotes'] += 1
    
    # Save the data to a CSV file
    save_engagement_data(engagement_data)
    
    return engagement_data
    
def save_engagement_data(engagement_data):
    """
    Save engagement data to a CSV file
    
    Args:
        engagement_data: Dictionary of engagement data
    """
    # Create directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data/engagers_{timestamp}.csv"
    
    # Write data to CSV
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['username', 'likes', 'replies', 'retweets', 'quotes', 'total_score']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        
        # Calculate scores based on env variables
        like_score = int(os.getenv("LIKE_SCORE", 1))
        reply_score = int(os.getenv("REPLY_SCORE", 5))
        retweet_score = int(os.getenv("RETWEET_SCORE", 10))
        quote_score = int(os.getenv("QUOTE_SCORE", 15))
        
        for username, data in engagement_data.items():
            total_score = (
                data['likes'] * like_score +
                data['replies'] * reply_score +
                data['retweets'] * retweet_score +
                data['quotes'] * quote_score
            )
            
            writer.writerow({
                'username': username,
                'likes': data['likes'],
                'replies': data['replies'],
                'retweets': data['retweets'],
                'quotes': data['quotes'],
                'total_score': total_score
            })
    
    print(f"Engagement data saved to {filename}")
    return filename

def run_analysis():
    """Run the analysis process"""
    look_back = int(os.getenv("LOOK_BACK", 20))
    
    # Initialize Twitter
    twitter = PersistentTwitter()
    twitter.initialize()
    
    # Run analysis
    analyze_engagement(twitter, look_back)
    
if __name__ == "__main__":
    run_analysis()
