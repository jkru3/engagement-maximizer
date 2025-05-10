import os
import json
import csv
import glob
from persistent_twitter import PersistentTwitter

def get_latest_engagement_file():
    """Get the most recent engagement data file"""
    files = glob.glob("data/engagers_*.csv")
    if not files:
        return None
    return max(files, key=os.path.getctime)

def load_whitelist():
    """Load whitelist from JSON file"""
    try:
        with open("whitelist.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Whitelist file not found. Creating empty whitelist.")
        with open("whitelist.json", "w") as f:
            json.dump([], f)
        return []

def load_blacklist():
    """Load blacklist from JSON file"""
    try:
        with open("blacklist.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Blacklist file not found. Creating empty blacklist.")
        with open("blacklist.json", "w") as f:
            json.dump([], f)
        return []

def load_engagement_data(file_path):
    """Load engagement data from CSV file"""
    engagement_data = []
    
    with open(file_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            engagement_data.append({
                'username': row['username'],
                'likes': int(row['likes']),
                'replies': int(row['replies']),
                'retweets': int(row['retweets']),
                'quotes': int(row['quotes']),
                'total_score': int(row['total_score'])
            })
    
    # Sort by total score in descending order
    engagement_data.sort(key=lambda x: x['total_score'], reverse=True)
    return engagement_data

def manage_list():
    """Manage Twitter list based on engagement data"""
    # Initialize Twitter
    twitter = PersistentTwitter()
    twitter.initialize()
    
    # Get list parameters
    target_list_link = os.getenv("TARGET_LIST_LINK")
    list_size = int(os.getenv("LIST_SIZE", 10))
    
    # Load whitelist and blacklist
    whitelist = load_whitelist()
    blacklist = load_blacklist()
    
    # Get current list members
    print(f"Fetching current members of list: {target_list_link}")
    current_members = twitter.get_list_members(target_list_link)
    print(f"Current list has {len(current_members)} members")
    
    # Find the latest engagement data file
    engagement_file = get_latest_engagement_file()
    if not engagement_file:
        print("No engagement data found. Please run 'analyze' first.")
        return
    
    print(f"Using engagement data from: {engagement_file}")
    engagement_data = load_engagement_data(engagement_file)
    
    # Calculate who to keep and who to add
    keep_list = []
    remove_list = []
    
    # First, handle whitelist - these are always kept
    for username in current_members:
        if username in whitelist:
            keep_list.append(username)
            
    # Then, filter out remaining users based on their engagement scores
    remaining_members = [username for username in current_members if username not in keep_list]
    remaining_slots = list_size - len(keep_list)
    
    # Create a list of potential candidates to add (not blacklisted, not already in list)
    candidates = [
        user for user in engagement_data 
        if user['username'] not in current_members and user['username'] not in blacklist
    ]
    
    # If we need to remove users to make room
    if len(remaining_members) > remaining_slots:
        # Create a map of current members to their engagement scores
        member_scores = {}
        for member in remaining_members:
            score = 0
            for user in engagement_data:
                if user['username'] == member:
                    score = user['total_score']
                    break
            member_scores[member] = score
        
        # Sort members by score
        sorted_members = sorted(member_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Keep the highest scoring ones
        for i, (username, _) in enumerate(sorted_members):
            if i < remaining_slots:
                keep_list.append(username)
            else:
                remove_list.append(username)
    else:
        # We can keep all current members
        keep_list.extend(remaining_members)
        remaining_slots -= len(remaining_members)
        
        # Add new high-scoring users if there are slots available
        for user in candidates:
            if remaining_slots > 0:
                keep_list.append(user['username'])
                remaining_slots -= 1
            else:
                break
    
    # Generate report
    print("\n--- LIST MANAGEMENT REPORT ---")
    print(f"Target list size: {list_size}")
    print(f"Current list size: {len(current_members)}")
    print(f"Whitelisted users (always kept): {whitelist}")
    
    print("\nRECOMMENDED ACTIONS:")
    
    if remove_list:
        print("\nUsers to remove:")
        for username in remove_list:
            # Find the score if available
            score = 0
            for user in engagement_data:
                if user['username'] == username:
                    score = user['total_score']
                    break
            print(f"  - {username} (Score: {score})")
    else:
        print("\nNo users need to be removed.")
    
    # Find users to add (who aren't already in the keep list)
    users_to_add = []
    remaining_slots = list_size - len(keep_list)
    
    for user in candidates:
        if user['username'] not in keep_list and remaining_slots > 0:
            users_to_add.append(user)
            remaining_slots -= 1
        if remaining_slots <= 0:
            break
    
    if users_to_add:
        print("\nUsers to add:")
        for user in users_to_add:
            print(f"  - {user['username']} (Score: {user['total_score']})")
    else:
        print("\nNo users need to be added.")
    
    print("\nResulting list would contain:")
    for username in keep_list + [user['username'] for user in users_to_add]:
        print(f"  - {username}")
    
    print("\nNote: Please manually update your Twitter list based on these recommendations.")

if __name__ == "__main__":
    manage_list()
