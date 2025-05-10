import os
import sys
import argparse
from dotenv import load_dotenv
from persistent_twitter import PersistentTwitter
from analyze import run_analysis
from manage_list import manage_list

def init_twitter():
    """Initialize Twitter browser instance"""
    print("Initializing Twitter browser session...")
    twitter = PersistentTwitter()
    twitter.initialize()
    print("Twitter browser session initialized successfully")
    return twitter

def main():
    """Main entry point for the application"""
    # Load environment variables
    load_dotenv()
    
    # Create directories if they don't exist
    os.makedirs('data', exist_ok=True)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Twitter Engagement Analyzer')
    parser.add_argument('command', choices=['init', 'analyze', 'manage_list'], 
                        help='Command to execute')
    
    args = parser.parse_args()
    
    # Execute the specified command
    if args.command == 'init':
        init_twitter()
    elif args.command == 'analyze':
        run_analysis()
    elif args.command == 'manage_list':
        manage_list()
    else:
        print(f"Unknown command: {args.command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
