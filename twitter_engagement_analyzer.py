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
import random
from datetime import datetime

class TwitterEngagementAnalyzer:
    def __init__(self):
        self.setup_driver()
        self.engagers_data = {}
        self.tweets_data = []
        self.start_time = time.time()
        self.MAX_SESSION_TIME = 1800  # 30 minutes max
        
    def setup_driver(self):
        """Set up the Selenium browser driver with more human-like settings"""
        chrome_options = Options()
        
        # DON'T use headless mode as it's more easily detected
        # chrome_options.add_argument("--headless")
        
        # Use a realistic window size
        chrome_options.add_argument("--window-size=1366,768")
        
        # Add randomization to window size
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

    def go_to_profile(self, profile_name=None):
        """Navigate to your Twitter profile with human-like behavior"""
        if not self.session_time_check():
            return False
            
        # Handle popup modal if present
        try:
            self.random_sleep(2, 4)
            
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
            
        if profile_name:
            # Direct navigation to profile URL is more reliable
            self.driver.get(f"https://twitter.com/{profile_name}")
            print(f"Navigating directly to profile: {profile_name}")
            self.random_sleep(2, 4)
            return True
        else:
            try:
                # Alternative approach: Use the URL for your own profile
                # This avoids click intercepted errors
                self.driver.get("https://twitter.com/home")
                self.random_sleep(2, 4)
                
                # Get the current username from the page
                try:
                    # Try to find elements that might contain the username
                    possible_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                                                               '[data-testid="SideNav_AccountSwitcher_Button"]')
                    if possible_elements:
                        # Get text from the side nav button
                        username_text = possible_elements[0].get_attribute('aria-label')
                        if username_text:
                            # Parse the username from the aria-label text
                            # Usually in format like "Account menu, @username"
                            username_parts = username_text.split('@')
                            if len(username_parts) > 1:
                                username = username_parts[1].strip()
                                self.driver.get(f"https://twitter.com/{username}")
                                print(f"Navigating to your profile: {username}")
                                self.random_sleep(2, 4)
                                return True
                except Exception as e:
                    print(f"Error extracting username: {e}")
                
                # Fallback: try going to profile using the UI
                try:
                    # Wait for the page to fully load
                    self.random_sleep(3, 5)
                    
                    # Try a more robust approach using JavaScript to click
                    profile_buttons = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="SideNav_AccountSwitcher_Button"]')
                    if profile_buttons:
                        # Use JavaScript to click since it bypasses overlay issues
                        self.driver.execute_script("arguments[0].click();", profile_buttons[0])
                        self.random_sleep(2, 3)
                        
                        # Now find and click the Profile option
                        profile_option = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, '//span[text()="Profile"]'))
                        )
                        
                        self.driver.execute_script("arguments[0].click();", profile_option)
                        self.random_sleep(2, 3)
                        return True
                    else:
                        # If button not found, try using nav links
                        nav_links = self.driver.find_elements(By.CSS_SELECTOR, 'nav a')
                        for link in nav_links:
                            if 'profile' in link.get_attribute('href').lower():
                                self.driver.execute_script("arguments[0].click();", link)
                                self.random_sleep(2, 3)
                                return True
                                
                        # Last resort: try direct URL with username from cookies/storage
                        self.driver.get("https://twitter.com/i/flow/login")
                        self.random_sleep(2, 3)
                        return True
                except Exception as e:
                    print(f"Error navigating via UI: {e}")
                
                print("Using fallback direct navigation to your profile page")
                # If the user provided their username when they ran the script
                # So just get it from the instantiation
                username = os.getenv("TWITTER_USERNAME")  # This is the username used at script start
                self.driver.get(f"https://twitter.com/{username}")
                self.random_sleep(2, 4)
                return True
                
            except Exception as e:
                print(f"Error navigating to profile: {e}")
                return False
                
    def get_top_tweets(self, count=50):  # Reduced from 100 to 50 for lower detection risk
        """Collect data from top tweets on the profile with human-like behavior"""
        if not self.session_time_check():
            return False
            
        try:
            # Random pause before interacting with the page
            self.random_sleep(1, 3)
            
            # Switch to Top Tweets view with natural delay
            try:
                tabs = self.driver.find_elements(By.CSS_SELECTOR, '[role="tablist"] [role="tab"]')
                
                # Random pause as if deciding which tab to click
                self.random_sleep(0.8, 2)
                
                # Click on the "Top" tab - usually the second tab
                top_tab_found = False
                for tab in tabs:
                    if "Top" in tab.text:
                        self.random_sleep(0.3, 0.8)
                        tab.click()
                        top_tab_found = True
                        break
                        
                if top_tab_found:
                    print("Switched to Top Tweets view")
                else:
                    print("Could not find Top Tweets tab, using current view")
                    
                self.random_sleep(1.5, 3)
            except Exception as e:
                print(f"Error switching to Top Tweets: {e}")
                print("Continuing with default view")
            
            tweets_analyzed = 0
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            previous_tweet_count = 0
            no_new_tweets_count = 0
            
            while tweets_analyzed < count:
                if not self.session_time_check():
                    print("Session time limit reached while collecting tweets.")
                    break
                    
                # Find all tweet elements
                tweet_elements = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="tweet"]')
                
                # If we're not finding new tweets after multiple scrolls, we might be at the end
                if len(tweet_elements) == previous_tweet_count:
                    no_new_tweets_count += 1
                    if no_new_tweets_count >= 3:
                        print(f"No new tweets found after several scrolls. Ending collection with {tweets_analyzed} tweets.")
                        break
                else:
                    no_new_tweets_count = 0
                    previous_tweet_count = len(tweet_elements)
                
                # Process new tweet elements
                for tweet in tweet_elements[tweets_analyzed:]:
                    if tweets_analyzed >= count:
                        break
                        
                    if not self.session_time_check():
                        break
                        
                    try:
                        # Scroll the tweet into view with human-like behavior
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tweet)
                        self.random_sleep(0.5, 1.5)
                        
                        # Sometimes hover over the tweet before extracting data (more human-like)
                        if random.random() < 0.3:
                            self.driver.execute_script("""
                                var element = arguments[0];
                                var mouseoverEvent = new MouseEvent('mouseover', {
                                    'view': window,
                                    'bubbles': true,
                                    'cancelable': true
                                });
                                element.dispatchEvent(mouseoverEvent);
                            """, tweet)
                            self.random_sleep(0.3, 1.2)
                        
                        # Extract tweet data
                        tweet_data = self._extract_tweet_data(tweet)
                        
                        if tweet_data:
                            self.tweets_data.append(tweet_data)
                            
                            # Print progress with some randomness in wording
                            progress_messages = [
                                f"Analyzed tweet {tweets_analyzed+1}/{count}: {tweet_data['text'][:25]}...",
                                f"Processing tweet {tweets_analyzed+1} of {count}: {tweet_data['text'][:25]}...",
                                f"Examining tweet {tweets_analyzed+1}/{count}: {tweet_data['text'][:25]}..."
                            ]
                            print(random.choice(progress_messages))
                            
                            tweets_analyzed += 1
                            
                            # Occasional longer pause as if reading the tweet
                            if random.random() < 0.2:
                                self.random_sleep(1, 3)
                            
                    except Exception as e:
                        print(f"Error processing tweet: {e}")
                        continue
                
                # If we haven't collected enough tweets, scroll down with human-like behavior
                if tweets_analyzed < count:
                    # Use human-like scrolling
                    self.human_like_scroll()
                    
                    # Random longer pause occasionally as if reading
                    if random.random() < 0.15:
                        self.random_sleep(2, 4)
                    else:
                        self.random_sleep(0.7, 2)
                    
                    new_height = self.driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        # Try one more scroll with different distance
                        self.human_like_scroll(random.randint(500, 1000))
                        self.random_sleep(1, 2)

                        new_height = self.driver.execute_script("return document.body.scrollHeight")
                        if new_height == last_height:
                            print(f"Reached end of timeline. Collected {tweets_analyzed} tweets.")
                            break
                        
                    last_height = new_height
            
            print(f"Successfully collected data from {len(self.tweets_data)} tweets")
            return True
            
        except Exception as e:
            print(f"Error collecting tweets: {e}")
            return False
            
    def _extract_tweet_data(self, tweet_element):
        """Extract data from a single tweet element"""
        try:
            # Extract tweet text
            try:
                text_element = tweet_element.find_element(By.CSS_SELECTOR, '[data-testid="tweetText"]')
                tweet_text = text_element.text
            except:
                # Some tweets might not have text (e.g., only images)
                tweet_text = "[No text content]"
            
            # Get tweet statistics
            stats = {'likes': 0, 'replies': 0, 'retweets': 0}
            try:
                stat_elements = tweet_element.find_elements(By.CSS_SELECTOR, '[role="group"] > div')
                
                for stat in stat_elements:
                    stat_text = stat.text.lower()
                    if "retweet" in stat_text:
                        stats['retweets'] = self._parse_stat_count(stat_text)
                    elif "like" in stat_text:
                        stats['likes'] = self._parse_stat_count(stat_text)
                    elif "repl" in stat_text:
                        stats['replies'] = self._parse_stat_count(stat_text)
            except Exception as e:
                print(f"Error parsing tweet stats: {e}")
                    
            # Get timestamp
            try:
                timestamp_element = tweet_element.find_element(By.CSS_SELECTOR, 'time')
                timestamp = timestamp_element.get_attribute('datetime')
            except:
                timestamp = None
            
            # Get tweet URL
            try:
                url_element = tweet_element.find_element(By.CSS_SELECTOR, 'a[href*="/status/"]')
                tweet_url = url_element.get_attribute('href')
                tweet_id = tweet_url.split('/')[-1]
            except:
                # Generate a random ID if we can't get the real one
                tweet_id = f"unknown_{random.randint(10000, 99999)}"
                tweet_url = None
            
            return {
                'tweet_id': tweet_id,
                'url': tweet_url,
                'text': tweet_text,
                'timestamp': timestamp,
                'likes': stats.get('likes', 0),
                'replies': stats.get('replies', 0),
                'retweets': stats.get('retweets', 0)
            }
            
        except Exception as e:
            print(f"Error extracting tweet data: {e}")
            return None
            
    def _parse_stat_count(self, stat_text):
        """Parse the count from a stat text (e.g., "5 Likes" -> 5)"""
        parts = stat_text.split()
        for part in parts:
            # Try to convert to integer
            try:
                return int(part.replace(',', ''))
            except ValueError:
                # If part contains K or M (e.g., 1.5K)
                if 'k' in part.lower():
                    return int(float(part.lower().replace('k', '')) * 1000)
                elif 'm' in part.lower():
                    return int(float(part.lower().replace('m', '')) * 1000000)
                    
        return 0
        
    def analyze_engagement(self, top_tweet_count=5):  # Reduced from 10 to 5 for lower detection risk
        """Analyze engagement for top tweets with human-like behavior"""
        if not self.session_time_check():
            return False
            
        print(f"Analyzing engagement for top {top_tweet_count} tweets...")
        
        # Sort tweets by likes
        sorted_tweets = sorted(self.tweets_data, key=lambda x: x['likes'], reverse=True)
        top_tweets = sorted_tweets[:top_tweet_count]
        
        # Add some randomness to the order (more human-like behavior)
        if random.random() < 0.3:
            random.shuffle(top_tweets)
            print("Analyzing tweets in random order for variety")
        
        for i, tweet in enumerate(top_tweets):
            if not self.session_time_check():
                print("Session time limit reached during engagement analysis.")
                break
                
            print(f"Analyzing engagement for tweet {i+1}/{top_tweet_count}")
            
            try:
                # Navigate to tweet URL with a human-like random delay
                self.random_sleep(1, 3)
                
                if tweet['url']:
                    self.driver.get(tweet['url'])
                    
                    # Random pause after page load as a human would
                    self.random_sleep(2, 4)
                    
                    # Mimic human reading behavior - scroll down slightly
                    self.human_like_scroll(random.randint(100, 300))
                    self.random_sleep(1, 3)
                    
                    # Click on likes to see who liked with natural delay
                    try:
                        # Try different ways to find likes button since Twitter's UI can vary
                        like_selectors = [
                            '//span[contains(text(), "Liked by")]',
                            '[data-testid="socialContext"]',
                            '[aria-label*="like"]'
                        ]
                        
                        likes_button = None
                        for selector in like_selectors:
                            try:
                                if selector.startswith('//'):
                                    likes_button = WebDriverWait(self.driver, 5).until(
                                        EC.element_to_be_clickable((By.XPATH, selector))
                                    )
                                else:
                                    likes_button = WebDriverWait(self.driver, 5).until(
                                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                                    )
                                break
                            except:
                                continue
                                
                        if likes_button:
                            # Slight pause before clicking, as a human would
                            self.random_sleep(0.5, 1.5)
                            
                            # Use JavaScript to click to avoid interception
                            self.driver.execute_script("arguments[0].click();", likes_button)
                            self.random_sleep(2, 4)
                            
                            # Collect names of users who liked
                            likers = self._collect_user_list()
                            
                            # Store engagement data
                            for user in likers:
                                if user not in self.engagers_data:
                                    self.engagers_data[user] = {'likes': 0, 'comments': 0}
                                self.engagers_data[user]['likes'] += 1
                            
                            # Go back to tweet with human-like delay
                            self.random_sleep(0.8, 2)
                            self.driver.back()
                            self.random_sleep(1.5, 3)
                        else:
                            print("Could not find likes button for this tweet")
                    except Exception as e:
                        print(f"Error accessing likes: {e}")
                    
                    # Now try to get comments/replies
                    # This is more complex as Twitter doesn't show a simple list of commenters
                    # We'll just scroll through replies and record users
                    try:
                        # Scroll to see replies
                        self.human_like_scroll(random.randint(300, 600))
                        self.random_sleep(1, 3)
                        
                        # Collect usernames of repliers
                        repliers = self._collect_repliers()
                        
                        # Store engagement data
                        for user in repliers:
                            if user not in self.engagers_data:
                                self.engagers_data[user] = {'likes': 0, 'comments': 0}
                            self.engagers_data[user]['comments'] += 1
                    except Exception as e:
                        print(f"Error processing replies: {e}")
                else:
                    print(f"No URL available for tweet: {tweet['text'][:30]}...")
                    
            except Exception as e:
                print(f"Error analyzing engagement for tweet: {e}")
                continue
                
        return True
        
    def _collect_user_list(self):
        """Collect usernames from a user list modal (likes, followers, etc.) with human-like behavior"""
        users = []
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        max_users = 50  # Reduced from 100 to 50 for lower detection risk
        scrolls_without_new_users = 0
        
        while len(users) < max_users and scrolls_without_new_users < 3:
            if not self.session_time_check():
                break
                
            # Find all reply elements
            reply_elements = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="tweet"]')
            
            # Track number of users before processing
            users_before = len(users)
            
            # Skip the first element as it's likely the original tweet
            for reply in reply_elements[1:]:
                try:
                    # Scroll the reply into view
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", reply)
                    
                    # Sometimes pause as if reading the reply
                    if random.random() < 0.15:
                        self.random_sleep(0.3, 1.5)
                        
                    username_element = reply.find_element(By.CSS_SELECTOR, '[data-testid="User-Name"]')
                    username_parts = username_element.text.split('\n')
                    
                    if len(username_parts) >= 2:
                        screen_name = username_parts[1].replace('@', '')
                        if screen_name not in users:
                            users.append(screen_name)
                except:
                    continue
                    
            # If we've found enough users or no new users were added, break
            if len(users) >= max_users:
                break
                
            # Check if we found new users
            if len(users) == users_before:
                scrolls_without_new_users += 1
            else:
                scrolls_without_new_users = 0
                
            # Scroll down with human-like behavior
            self.human_like_scroll()
            
            # Sometimes pause longer as if reading the replies
            if random.random() < 0.2:
                self.random_sleep(1.5, 3)
            else:
                self.random_sleep(0.7, 2)
                
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                scrolls_without_new_users += 1
                
            last_height = new_height
            
        return users
        
    def save_results(self):
        """Save analysis results to CSV files"""
        # Create directory for results
        os.makedirs("twitter_analysis", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save tweets data
        tweets_file = f"twitter_analysis/tweets_{timestamp}.csv"
        with open(tweets_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['tweet_id', 'url', 'text', 'timestamp', 'likes', 'replies', 'retweets'])
            writer.writeheader()
            for tweet in self.tweets_data:
                writer.writerow(tweet)
                
        # Save engagers data
        engagers_file = f"twitter_analysis/engagers_{timestamp}.csv"
        with open(engagers_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['username', 'likes', 'comments', 'total_engagement'])
            
            # Sort engagers by total engagement
            sorted_engagers = sorted(
                self.engagers_data.items(), 
                key=lambda x: x[1]['likes'] + x[1]['comments'], 
                reverse=True
            )
            
            for username, data in sorted_engagers:
                total = data['likes'] + data['comments']
                writer.writerow([username, data['likes'], data['comments'], total])
                
        print(f"Results saved to:\n- {tweets_file}\n- {engagers_file}")
        
        return {
            'tweets_file': tweets_file,
            'engagers_file': engagers_file
        }
        
    def analyze_top_engagers(self, export=True):
        """Find and print top engagers with human-like analysis patterns"""
        if not self.engagers_data:
            print("No engagement data available. Run analyze_engagement() first.")
            return
            
        # Sort engagers by total engagement
        sorted_engagers = sorted(
            self.engagers_data.items(), 
            key=lambda x: x[1]['likes'] + x[1]['comments'], 
            reverse=True
        )
        
        # Print top 20 engagers or fewer if we don't have that many
        top_count = min(20, len(sorted_engagers))
        print(f"\n===== TOP {top_count} ENGAGERS =====")
        print(f"{'Username':<20} {'Likes':<10} {'Comments':<10} {'Total':<10}")
        print("-" * 50)
        
        for i, (username, data) in enumerate(sorted_engagers[:top_count]):
            total = data['likes'] + data['comments']
            print(f"{username:<20} {data['likes']:<10} {data['comments']:<10} {total:<10}")
            
        # Optionally export to a nice formatted Excel file
        if export:
            try:
                os.makedirs("twitter_analysis", exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                # Create pandas DataFrame for easier formatting
                df = pd.DataFrame([
                    {
                        'Username': username,
                        'Likes': data['likes'],
                        'Comments': data['comments'],
                        'Total Engagement': data['likes'] + data['comments']
                    }
                    for username, data in sorted_engagers
                ])
                
                # Save to Excel for better formatting
                excel_file = f"twitter_analysis/top_engagers_{timestamp}.xlsx"
                df.to_excel(excel_file, index=False)
                print(f"\nDetailed engager analysis saved to: {excel_file}")
                
                return excel_file
            except Exception as e:
                print(f"Error exporting to Excel: {e}")
                print("Results are still available in CSV format.")
                
        return None
        
    def clean_up(self):
        """Perform a clean exit with human-like behavior"""
        # Random delay before closing as a human might do
        self.random_sleep(1, 3)
        
        # Go to Twitter homepage before closing (more natural exit pattern)
        try:
            self.driver.get("https://twitter.com/home")
            self.random_sleep(2, 4)
        except:
            pass
            
        # Close the browser
        self.driver.quit()
        print("Browser closed and session ended normally.")
        
    def close(self):
        """Close the browser and clean up"""
        self.clean_up()

    def _collect_repliers(self):
        """Collect usernames of people who replied to a tweet with human-like behavior"""
        users = []
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        max_users = 30  # Reduced from 50 to 30 for lower detection risk
        scrolls_without_new_users = 0
        
        while len(users) < max_users and scrolls_without_new_users < 3:
            if not self.session_time_check():
                break
                
            # Find all user elements
            user_elements = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="UserCell"]')
            
            # Track number of users before processing
            users_before = len(users)
            
            for user_element in user_elements:
                try:
                    username_element = user_element.find_element(By.CSS_SELECTOR, '[data-testid="User-Name"]')
                    username_parts = username_element.text.split('\n')
                    
                    if len(username_parts) >= 2:
                        screen_name = username_parts[1].replace('@', '')
                        if screen_name not in users:
                            users.append(screen_name)
                            
                            # Sometimes pause as if reading the user profile
                            if random.random() < 0.1:
                                self.random_sleep(0.3, 1.2)
                except:
                    continue
                    
            # If we've found enough users or no new users were added, break
            if len(users) >= max_users:
                break
                
            # Check if we found new users
            if len(users) == users_before:
                scrolls_without_new_users += 1
            else:
                scrolls_without_new_users = 0
                
            # Scroll down modal with human-like behavior
            try:
                # Find the modal (different selectors depending on Twitter's current UI)
                modal_selectors = [
                    '[aria-label="Timeline: Liked by"]',
                    '[aria-modal="true"]',
                    '.css-1dbjc4n[role="dialog"]'
                ]
                
                modal = None
                for selector in modal_selectors:
                    try:
                        modal = self.driver.find_element(By.CSS_SELECTOR, selector)
                        break
                    except:
                        continue
                
                if modal:
                    # Human-like scrolling in the modal
                    current_scroll = self.driver.execute_script("return arguments[0].scrollTop", modal)
                    scroll_amount = random.randint(300, 500)
                    
                    # Scroll in incremental steps
                    steps = random.randint(4, 8)
                    for i in range(steps):
                        increment = scroll_amount / steps
                        current_scroll += increment
                        self.driver.execute_script("arguments[0].scrollTop = arguments[1]", modal, current_scroll)
                        time.sleep(random.uniform(0.05, 0.15))
                        
                    # Sometimes pause as if reading
                    if random.random() < 0.2:
                        self.random_sleep(0.8, 2)
                    else:
                        self.random_sleep(0.3, 1)
                else:
                    # Fallback to window scrolling if modal not found
                    self.human_like_scroll()
                    self.random_sleep(1, 2)
            except Exception as e:
                print(f"Error scrolling modal: {e}")
                # Fallback to window scrolling
                self.human_like_scroll()
                self.random_sleep(1, 2)
                
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                scrolls_without_new_users += 1
                
            last_height = new_height
            
        return users

if __name__ == "__main__":
    # Example usage
    analyzer = TwitterEngagementAnalyzer()
    
    # Replace with your Twitter credentials
    username = os.getenv("TWITTER_USERNAME")
    password = os.getenv("TWITTER_PASSWORD")
    
    try:
        print("Twitter Engagement Analyzer")
        print("===========================")
        print("This tool will help you identify who engages most with your Twitter content.")
        print("Note: Use responsibly and at a reasonable frequency to respect Twitter's terms.\n")
        
        print("Starting browser and navigating to Twitter...")
        if analyzer.login_to_twitter(username, password):
            # Navigate to your profile (or specify a profile name)
            print("\nNavigating to your profile...")
            # Use the username directly to avoid the UI navigation issues
            if analyzer.go_to_profile(username):
            
                # Collect data from top tweets (reduced count for lower detection risk)
                print("\nAnalyzing your tweets...")
                analyzer.get_top_tweets(count=50)
                
                if len(analyzer.tweets_data) > 0:
                    # Analyze engagement for top tweets (reduced count for lower detection risk)
                    print("\nAnalyzing engagement patterns...")
                    analyzer.analyze_engagement(top_tweet_count=5)
                    
                    # Save results to CSV
                    print("\nSaving results...")
                    analyzer.save_results()
                    
                    # Print/export top engagers
                    analyzer.analyze_top_engagers()
                    
                    print("\nAnalysis complete! Check the 'twitter_analysis' folder for your results.")
                else:
                    print("No tweets found to analyze. Please check your profile or try different parameters.")
    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Cleaning up...")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        # Always close the browser when done
        print("\nShutting down browser...")
        analyzer.close()