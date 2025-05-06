from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
import csv
import os
import json
import random
from datetime import datetime
from dotenv import load_dotenv

class TwitterListManager:
    '''
    helps you manage your Twitter lists based on engagement data
    '''
    def __init__(self):
        self.setup_driver()
        self.list_members = []
        self.top_engagers = []
        self.whitelist = []
        self.max_list_size = 100  # Default, will be updated from user input
        self.start_time = time.time()
        self.MAX_SESSION_TIME = 1800  # 30 minutes max
        
    def setup_driver(self):
        """Set up the Selenium browser driver with more human-like settings"""
        chrome_options = Options()
        
        # Use a realistic window size
        width = random.randint(1200, 1600)
        height = random.randint(700, 900)
        chrome_options.add_argument(f"--window-size={width},{height}")
        
        # Disable automation flags
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Add a user agent that looks more like a regular browser
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
        ]
        chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")
        
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        # Execute the stealth JS script to hide webdriver usage
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
            """
        })
        
    def random_sleep(self, min_seconds=1, max_seconds=5):
        """Sleep for a random amount of time between actions to appear more human-like"""
        sleep_time = random.uniform(min_seconds, max_seconds)
        time.sleep(sleep_time)
        
    def human_like_scroll(self, distance=None, direction="down"):
        """Scroll in a more human-like pattern"""
        if not distance:
            # Random scroll distance if none provided
            distance = random.randint(300, 800)
            
        current_position = self.driver.execute_script("return window.pageYOffset;")
        
        if direction == "down":
            target_position = current_position + distance
        else:
            target_position = max(0, current_position - distance)
            
        # Scroll in small increments with varying speeds to mimic human behavior
        steps = random.randint(5, 12)
        for i in range(steps):
            increment = (target_position - current_position) / steps
            current_position += increment
            self.driver.execute_script(f"window.scrollTo(0, {int(current_position)});")
            
            # Random small pause between scroll increments
            time.sleep(random.uniform(0.01, 0.1))
            
        # Occasionally scroll back up slightly as humans do when reading
        if random.random() < 0.3 and direction == "down":
            small_scroll_back = random.randint(20, 100)
            self.driver.execute_script(f"window.scrollTo(0, {int(current_position - small_scroll_back)});")
            
        # Sometimes pause as if reading content
        if random.random() < 0.4:
            self.random_sleep(1, 3)
        
    def session_time_check(self):
        """Check if we've exceeded the maximum session time"""
        if time.time() - self.start_time > self.MAX_SESSION_TIME:
            print("Maximum session time reached. Exiting safely.")
            return False
        return True
        
    def login_to_twitter(self, username, password):
        """Log in to Twitter with human-like behavior"""
        self.driver.get("https://twitter.com/login")
        print("Navigating to Twitter login page...")
        self.random_sleep(2, 4)
        
        try:
            # Find username input field and enter username
            username_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[autocomplete="username"]'))
            )
            
            # Type username with variable speed like a human
            for char in username:
                username_input.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
                
            self.random_sleep(0.5, 1.5)
            
            # Click the Next button
            next_button = self.driver.find_element(By.XPATH, '//span[contains(text(), "Next")]')
            
            # Slight pause before clicking like a human would
            self.random_sleep(0.3, 0.8)
            next_button.click()
            self.random_sleep(1, 2)
            
            # Find password input field and enter password
            password_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="password"]'))
            )
            
            # Type password with variable speed like a human
            for char in password:
                password_input.send_keys(char)
                time.sleep(random.uniform(0.05, 0.2))
                
            self.random_sleep(0.7, 1.5)
            
            # Click the Login button
            login_button = self.driver.find_element(By.XPATH, '//span[contains(text(), "Log in")]')
            
            # Slight pause before clicking the login button
            self.random_sleep(0.3, 0.8)
            login_button.click()
            
            print("Login attempted. Waiting for page to load...")
            self.random_sleep(3, 6)  # Wait for login to complete
            
            # Check if we need to handle any security prompts
            if "login" in self.driver.current_url.lower():
                print("Login may require additional verification. Please check the browser.")
                input("Press Enter once you've manually completed verification...")
            
        except Exception as e:
            print(f"Error during login: {e}")
            return False
            
        return True

    def handle_popups(self):
        """Handle any popups that might appear"""
        try:
            # Check for potential modals/overlays and dismiss them
            overlay_selectors = [
                '[data-testid="mask"]',
                '[role="dialog"]',
                '[aria-modal="true"]'
            ]
            
            for selector in overlay_selectors:
                try:
                    overlay = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    # Try to click the 'X' button or just click elsewhere to dismiss
                    try:
                        close_button = self.driver.find_element(By.CSS_SELECTOR, '[data-testid="Button"]')
                        close_button.click()
                        self.random_sleep(1, 2)
                    except:
                        # Click outside the modal (escape key might also work)
                        action = webdriver.ActionChains(self.driver)
                        action.move_by_offset(10, 10).click().perform()
                        self.random_sleep(1, 2)
                        self.driver.find_element(By.TAG_NAME, 'body').send_keys(webdriver.Keys.ESCAPE)
                        self.random_sleep(1, 2)
                except:
                    continue
        except:
            pass

    def load_top_engagers(self, engagers_file):
        """Load top engager data from the CSV file"""
        print(f"Loading top engagers from: {engagers_file}")
        
        try:
            self.top_engagers = []
            df = pd.read_csv(engagers_file)
            
            # Ensure the dataframe has the expected columns
            if 'username' not in df.columns:
                print("Error: CSV file doesn't have the expected 'username' column")
                return False
                
            # Convert dataframe to list of usernames
            self.top_engagers = df['username'].tolist()
            print(f"Loaded {len(self.top_engagers)} top engagers")
            return True
        except Exception as e:
            print(f"Error loading engagers file: {e}")
            return False

    def load_whitelist(self, whitelist_file):
        """Load whitelist of profiles from JSON file"""
        print(f"Loading whitelist from: {whitelist_file}")
        
        try:
            with open(whitelist_file, 'r') as f:
                whitelist_data = json.load(f)
                
            if isinstance(whitelist_data, list):
                self.whitelist = whitelist_data
            else:
                # Try to extract profiles from a potential JSON structure
                if 'profiles' in whitelist_data:
                    self.whitelist = whitelist_data['profiles']
                else:
                    # Just use all values as a fallback
                    self.whitelist = list(whitelist_data.values())
                    
            print(f"Loaded {len(self.whitelist)} whitelisted profiles")
            return True
        except Exception as e:
            print(f"Error loading whitelist file: {e}")
            print("Creating empty whitelist")
            self.whitelist = []
            return True  # Return True so the program can continue

    def fetch_list_members(self, list_url):
        """Fetch members of the Twitter list"""
        print(f"Navigating to list: {list_url}")
        
        if not self.session_time_check():
            return False
            
        try:
            self.driver.get(list_url)
            self.random_sleep(3, 5)
            
            # Handle any popups that might appear
            self.handle_popups()
            
            # Wait for members to load
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="UserCell"]'))
                )
            except TimeoutException:
                print("List members not found. Checking if we're on the correct page...")
                # Check if we need to click on "Members" tab
                try:
                    members_tab = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, '//span[text()="Members"]'))
                    )
                    members_tab.click()
                    self.random_sleep(2, 4)
                except:
                    print("Members tab not found. This may not be a list page.")
                    
            # Now collect list members
            print("Collecting list members...")
            self.list_members = []
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            max_scroll_attempts = 30  # Limit scrolling to avoid infinite loop
            scroll_attempts = 0
            
            while scroll_attempts < max_scroll_attempts:
                if not self.session_time_check():
                    break
                    
                # Get user cells
                user_cells = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="UserCell"]')
                
                # Extract usernames
                for cell in user_cells:
                    try:
                        username_element = cell.find_element(By.CSS_SELECTOR, '[data-testid="User-Name"]')
                        username_parts = username_element.text.split('\n')
                        
                        if len(username_parts) >= 2:
                            screen_name = username_parts[1].replace('@', '')
                            if screen_name not in self.list_members:
                                self.list_members.append(screen_name)
                    except:
                        continue
                        
                print(f"Found {len(self.list_members)} list members so far...")
                
                # Scroll down to load more
                self.human_like_scroll(random.randint(500, 800))
                self.random_sleep(1, 3)
                
                # Check if we've reached the end
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    # Try one more scroll to confirm
                    self.human_like_scroll(random.randint(200, 500))
                    self.random_sleep(1, 2)
                    
                    new_height = self.driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        print("Reached end of list members")
                        break
                        
                last_height = new_height
                scroll_attempts += 1
                
            print(f"Collected {len(self.list_members)} list members in total")
            return True
            
        except Exception as e:
            print(f"Error fetching list members: {e}")
            return False

    def analyze_list(self):
        """Analyze the list and generate recommendations for adding/removing members"""
        if not self.top_engagers or not self.list_members:
            print("Error: Top engagers or list members missing. Cannot analyze.")
            return False
        
        print("\n===== LIST ANALYSIS =====")
        print(f"Current list size: {len(self.list_members)}")
        print(f"Target list size: {self.max_list_size}")
        print(f"Whitelisted profiles: {len(self.whitelist)}")
        
        # Calculate available slots for non-whitelisted profiles
        available_slots = self.max_list_size - len(self.whitelist)
        print(f"Available slots for non-whitelisted profiles: {available_slots}")
        
        # Identify whitelisted profiles that are not in the list (need to be added)
        whitelist_not_in_list = [profile for profile in self.whitelist if profile not in self.list_members]
        if whitelist_not_in_list:
            print(f"\n{len(whitelist_not_in_list)} whitelisted profiles are not in the list and should be added:")
            for profile in whitelist_not_in_list:
                print(f"- @{profile}")
        
        # Identify top engagers who are not in the list and not whitelisted
        top_engagers_to_add = []
        for engager in self.top_engagers:
            if engager not in self.list_members and engager not in self.whitelist:
                top_engagers_to_add.append(engager)
                if len(top_engagers_to_add) >= available_slots:
                    break
        
        # Identify list members who are not top engagers and not whitelisted (candidates for removal)
        list_members_to_remove = []
        for member in self.list_members:
            if member not in self.whitelist and member not in self.top_engagers[:available_slots]:
                list_members_to_remove.append(member)
        
        # Generate recommendations
        print("\n===== RECOMMENDATIONS =====")
        
        # Profiles to add
        add_count = min(len(top_engagers_to_add), available_slots)
        if add_count > 0:
            print(f"\nRECOMMENDED TO ADD ({add_count} profiles):")
            for i, profile in enumerate(top_engagers_to_add[:add_count]):
                rank = self.top_engagers.index(profile) + 1
                print(f"{i+1}. @{profile} (Engager Rank: {rank})")
        else:
            print("\nNo profiles recommended to add")
            
        # Profiles to remove
        current_non_whitelist = len(self.list_members) - len([m for m in self.list_members if m in self.whitelist])
        remove_count = max(0, current_non_whitelist - available_slots)
        
        if remove_count > 0:
            print(f"\nRECOMMENDED TO REMOVE ({remove_count} profiles):")
            for i, profile in enumerate(list_members_to_remove[:remove_count]):
                try:
                    rank = self.top_engagers.index(profile) + 1
                    rank_info = f"(Engager Rank: {rank})"
                except ValueError:
                    rank_info = "(Not in top engagers)"
                    
                print(f"{i+1}. @{profile} {rank_info}")
        else:
            print("\nNo profiles recommended to remove")
            
        return True

    def close(self):
        """Close the browser and clean up"""
        # Random delay before closing as a human might do
        self.random_sleep(1, 3)
        
        # Close the browser
        self.driver.quit()
        print("Browser closed and session ended normally.")

# Main execution function
def main(username, password, list_link, engagers_file, whitelist_file=None, list_size=100):
    manager = TwitterListManager()
    
    try:
        # Set the max list size
        manager.max_list_size = int(list_size)
            
        # Load top engagers
        if not manager.load_top_engagers(engagers_file):
            print("Failed to load top engagers. Exiting.")
            manager.close()
            return
            
        # Load whitelist if provided
        if whitelist_file:
            manager.load_whitelist(whitelist_file)
            
        # Log in to Twitter
        print("\nLogging in to Twitter...")
        if not manager.login_to_twitter(username, password):
            print("Failed to log in. Exiting.")
            manager.close()
            return
            
        # Fetch list members
        print("\nFetching list members...")
        if not manager.fetch_list_members(list_link):
            print("Failed to fetch list members. Exiting.")
            manager.close()
            return
            
        # Analyze the list and generate recommendations
        manager.analyze_list()
        
    except KeyboardInterrupt:
        print("\nOperation interrupted by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        # Always close the browser
        manager.close()

if __name__ == "__main__":
    # Configuration - hardcoded for convenience
    load_dotenv()
    username = os.getenv("TWITTER_USERNAME")
    password = os.getenv("TWITTER_PASSWORD")
    listlink = os.getenv("TARGET_LIST_LINK")
    listsize = 100  # Maximum number of profiles in the list
    
    # You can update these paths as needed
    engagers_file = "twitter_analysis/engagers_20250505_134849.csv"  # Update this path
    whitelist_file = "whitelist.json"  # Update or set to None if not using
    
    main(username, password, listlink, engagers_file, whitelist_file, listsize)