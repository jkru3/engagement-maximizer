# Twitter Engagement Analyzer

TODO:
- [ ] phase 1:
    - [ ] persist your authentication session between test runs
    - [ ] understand/clean twitter_list_manager
    - [ ] get working
    - [ ] take in MOST RECENT engagers file
    - [ ] engagement files by score, passable as a parameter (replies == 5 likes, reposts == 15 likes)
- [ ] phase 2:
    - [ ] persist your authentication session between test runs
    - [ ] accurately look at engagement the way a human would
        - [ ] replies
        - [ ] likes + retweets
    - [ ] set a limit to how far back you want to look (5 tweets to start)
    - [ ] skip ads
- [ ] phase 3:
    - [ ] make a video:
        - no more screaming into the void
        - build communities around actual engagement from real people, NOT AI
        - spend less time on social media, get more out of it
 
## User Documentation

This documentation provides detailed instructions for using the Twitter Engagement Analyzer tool to track who's engaging with your Twitter posts without using the Twitter API.

### Table of Contents

1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Running the Script](#running-the-script)
6. [Understanding the Output](#understanding-the-output)
7. [Customization Options](#customization-options)
8. [Risk Mitigation](#risk-mitigation)
9. [Troubleshooting](#troubleshooting)
10. [Advanced Usage](#advanced-usage)

## Introduction

The Twitter Engagement Analyzer is a Python-based tool that uses browser automation to help you identify who is engaging with your Twitter content most frequently. The script logs into your Twitter account, navigates to your profile, analyzes your top tweets, and identifies users who regularly like, comment, or otherwise engage with your content.

This tool was designed for personal use by account owners who want to better understand their engagement patterns without purchasing Twitter's expensive API access.

## Prerequisites

Before using this tool, you'll need:

- Python 3.7 or newer
- Chrome browser installed
- A valid Twitter account with login credentials. You need to be logged in to see who has been liking your posts
- Basic familiarity with running Python scripts

## Installation

### Step 1: Install Python

If you don't already have Python installed:
- Download from [python.org](https://www.python.org/downloads/)
- Enable the "Add Python to PATH" option during installation

### Step 2: Install Required Libraries

Open a command prompt or terminal and run:

```
pip install selenium pandas webdriver-manager openpyxl
```

### Step 3: Download the Script

- Create a new folder for this project (e.g., "twitter-analyzer")
- Save the Python script from the previous artifact as `twitter_engagement_analyzer.py` in this folder

## Configuration

### Required Modifications

Before running the script, you must edit the following configurations at the bottom of the file:

```python
# Replace with your Twitter credentials
username = "your_username"  # Your Twitter username or email
password = "your_password"  # Your Twitter password

# Additional configuration options
profile_name = None  # Set to your Twitter handle if login navigation fails
tweet_count = 100    # Number of tweets to analyze
top_tweet_count = 10 # Number of top tweets to analyze engagement for
```

### Optional Modifications

You can further customize the script by editing these parameters:

```python
# Browser settings
chrome_options = Options()
# Uncomment to run without browser UI (headless mode):
# chrome_options.add_argument("--headless")
```

For headless operation (no visible browser), uncomment the indicated line.

## Running the Script

### First Run

1. Open a terminal/command prompt
2. Navigate to your project directory:
   ```
   cd path/to/twitter-analyzer
   ```
3. Run the script:
   ```
   python twitter_engagement_analyzer.py
   ```

### What to Expect

- A Chrome window will open and navigate to Twitter
- The script will log in using your credentials
- It will navigate to your profile
- It will collect data from your top tweets
- It will analyze engagement patterns
- Results will be saved to CSV files in a "twitter_analysis" folder

## Understanding the Output

The script generates three main output files:

### 1. tweets_[timestamp].csv

Contains information about each analyzed tweet:
- tweet_id: The unique ID of the tweet
- url: Direct link to the tweet
- text: Content of the tweet
- timestamp: When the tweet was posted
- likes: Number of likes received
- replies: Number of replies received
- retweets: Number of retweets received

### 2. engagers_[timestamp].csv

Contains information about users who engaged with your content:
- username: Twitter handle of the user
- likes: Number of times they liked your analyzed tweets
- comments: Number of times they commented on your analyzed tweets
- total_engagement: Combined engagement count

### 3. top_engagers_[timestamp].xlsx

An Excel file with formatted and sorted engagement data, making it easy to identify your most active followers.

## Customization Options

### Analyzing More Tweets

To analyze more than the default 100 tweets, modify:

```python
analyzer.get_top_tweets(count=200)  # Increase to desired number
```

### Focusing on Recent Tweets

To focus on your most recent tweets rather than top tweets, modify the `get_top_tweets` method:

```python
def get_top_tweets(self, count=100):
    try:
        # Instead of clicking Top Tweets tab, just use the default (latest)
        # Remove or comment out the following 4 lines:
        # top_tweets_tab = WebDriverWait(self.driver, 10).until(
        #     EC.element_to_be_clickable((By.XPATH, '//span[text()="Top"]'))
        # )
        # top_tweets_tab.click()
        # print("Switched to Top Tweets view")
        # time.sleep(3)
        
        # Rest of the method remains the same...
```

### Adding More Metrics

To track additional engagement metrics, modify the `_extract_tweet_data` method to capture other statistics.

## Risk Mitigation

To minimize detection risk, consider these modifications:

### Add Random Delays

```python
import random

# Add this function to the class
def random_sleep(self, min_seconds=1, max_seconds=5):
    """Sleep for a random amount of time between actions"""
    time.sleep(random.uniform(min_seconds, max_seconds))

# Then replace fixed sleep times with random sleeps
# For example, change:
# time.sleep(2)
# To:
# self.random_sleep(1, 3)
```

### Mimic Human Navigation

Add mouse movement and scrolling patterns that mimic human behavior:

```python
def simulate_human_scroll(self):
    """Scroll in a more human-like pattern"""
    height = self.driver.execute_script("return document.body.scrollHeight")
    for i in range(10):
        # Scroll to random positions
        random_scroll = random.randint(100, height-100)
        self.driver.execute_script(f"window.scrollTo(0, {random_scroll});")
        self.random_sleep(0.5, 1.5)
    # Finally scroll to bottom
    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
```

### Limit Session Duration

Add a time limit to your analysis sessions:

```python
import time

start_time = time.time()
MAX_SESSION_TIME = 1800  # 30 minutes in seconds

# Add checks throughout the code:
if time.time() - start_time > MAX_SESSION_TIME:
    print("Session time limit reached. Exiting safely.")
    break
```

## Troubleshooting

### Login Issues

If the script can't log in to your account:
- Verify your username and password are correct
- Check if Twitter is requesting additional verification
- Try logging in manually first, then run the script

### Navigation Problems

If the script can't find elements:
- Twitter may have updated its UI
- Try updating the XPath or CSS selectors in the code
- Increase wait times with `WebDriverWait` parameters

### Engagement Analysis Errors

If engagement analysis fails:
- Twitter may have changed how likes or comments are displayed
- Try updating the relevant selectors in the code
- Reduce the number of tweets analyzed to identify the problem

## Advanced Usage

### Scheduling Regular Analysis

To run the script automatically on a schedule:

#### Windows (Task Scheduler):

1. Create a batch file (run_analysis.bat):
   ```
   cd C:\path\to\twitter-analyzer
   python twitter_engagement_analyzer.py
   ```
2. Open Task Scheduler and create a new task
3. Set the trigger (e.g., weekly)
4. Set the action to run the batch file

#### Mac/Linux (Cron):

1. Open terminal and type `crontab -e`
2. Add a line like:
   ```
   0 9 * * 1 cd /path/to/twitter-analyzer && python twitter_engagement_analyzer.py
   ```
   (This runs every Monday at 9 AM)

### Exporting to Other Formats

To export data in different formats, add functions like:

```python
def export_to_json(self):
    """Export engagement data to JSON format"""
    import json
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file = f"twitter_analysis/engagers_{timestamp}.json"
    
    with open(json_file, 'w') as f:
        json.dump(self.engagers_data, f, indent=4)
        
    print(f"JSON data exported to: {json_file}")
```

### Engagement Visualization

To add data visualization:

```python
def visualize_engagement(self):
    """Create visualizations of engagement data"""
    import matplotlib.pyplot as plt
    
    # Sort engagers by total engagement
    sorted_engagers = sorted(
        self.engagers_data.items(), 
        key=lambda x: x[1]['likes'] + x[1]['comments'], 
        reverse=True
    )[:10]  # Top 10
    
    usernames = [x[0] for x in sorted_engagers]
    likes = [x[1]['likes'] for x in sorted_engagers]
    comments = [x[1]['comments'] for x in sorted_engagers]
    
    plt.figure(figsize=(12, 6))
    plt.bar(usernames, likes, label='Likes')
    plt.bar(usernames, comments, bottom=likes, label='Comments')
    plt.title('Top 10 Engagers')
    plt.xlabel('Username')
    plt.ylabel('Engagement Count')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    plt.savefig(f"twitter_analysis/top_engagers_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
    plt.close()
```

### Analyzing Content Patterns

To analyze what types of content get the most engagement:

```python
def analyze_content_patterns(self):
    """Analyze content patterns in top tweets"""
    # Implement content pattern analysis based on tweet text
    # For example, checking for hashtags, keywords, etc.
    # And correlating with engagement metrics
```

Remember to run the script responsibly and respect Twitter's usage policies to maintain a positive social media presence.
