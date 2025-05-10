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

This tool helps you identify who engages with your Twitter content most frequently. It analyzes your recent tweets and provides recommendations for who to add to or remove from a Twitter list based on engagement patterns.

## Features

- **Analyze**: Looks at your recent tweets and tracks who has liked, replied, retweeted, or quoted them
- **Manage List**: Provides recommendations for who to add to or remove from a Twitter list based on engagement scores
- **Persistence**: Maintains a persistent browser session between commands

## Setup

1. Clone this repository
2. Install the requirements:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file with the following variables:
   ```
   TWITTER_USERNAME=your_twitter_username
   TWITTER_PASSWORD=your_twitter_password
   TARGET_LIST_LINK=https://twitter.com/i/lists/your_list_id
   LOOK_BACK=20
   LIST_SIZE=10
   LIKE_SCORE=1
   REPLY_SCORE=5
   RETWEET_SCORE=10
   QUOTE_SCORE=15
   ```
4. Create `whitelist.json` and `blacklist.json` files (if you want to use them):
   ```json
   [
       "elonmusk",
       "sama",
       "naval"
   ]
   ```

## Usage

1. Initialize a Twitter session:
   ```
   python main.py init
   ```
   This starts Chrome in the background with your Twitter account logged in.

2. Analyze your tweets:
   ```
   python main.py analyze
   ```
   This will connect to the existing Chrome instance and analyze your tweets.

3. Get list management recommendations:
   ```
   python main.py manage_list
   ```
   This will connect to the existing Chrome instance and provide list recommendations.

## How Browser Persistence Works

This tool launches Chrome as a separate process that continues running in the background even after the Python script completes. The next time you run a command, it will connect to the existing Chrome instance instead of starting a new one. This approach:

1. Keeps you logged in between commands
2. Makes commands run much faster
3. Avoids the overhead of starting a new browser each time

The Chrome process will keep running until you close it manually or restart your computer.