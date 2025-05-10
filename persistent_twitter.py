import os
import time
import json
import subprocess
import signal
import psutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class PersistentTwitter:
    def __init__(self):
        self.browser = None
        self.pid_file = "chrome_pid.txt"
        self.port_file = "chrome_port.txt"
        self.username = os.getenv("TWITTER_USERNAME")
        self.password = os.getenv("TWITTER_PASSWORD")
        self.port = 9222
        
    def is_browser_running(self):
        """Check if a browser instance is already running by checking the PID file"""
        if not os.path.exists(self.pid_file) or not os.path.exists(self.port_file):
            return False
            
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
                
            with open(self.port_file, 'r') as f:
                self.port = int(f.read().strip())
                
            # Check if process with this PID exists
            try:
                process = psutil.Process(pid)
                return process.is_running() and "chrome" in process.name().lower()
            except psutil.NoSuchProcess:
                return False
        except (ValueError, FileNotFoundError):
            return False
    
    def connect_to_existing_browser(self):
        """Attempt to connect to an existing Chrome browser instance"""
        try:
            # Attempt to connect to the existing browser using Chrome DevTools Protocol
            print(f"Attempting to connect to existing Chrome instance on port {self.port}")
            options = Options()
            options.add_experimental_option("debuggerAddress", f"127.0.0.1:{self.port}")
            self.browser = webdriver.Chrome(options=options)
            print("Successfully connected to existing browser instance")
            return True
        except Exception as e:
            print(f"Failed to connect to existing browser: {e}")
            return False
    
    def start_new_browser(self):
        """Start a new Chrome browser instance and save its PID"""
        try:
            # Find an available port
            self.port = self._find_available_port(start_port=9222)
            
            # Start Chrome with remote debugging enabled
            user_data_dir = os.path.abspath("chrome_user_data")
            os.makedirs(user_data_dir, exist_ok=True)
            
            chrome_executable = self._find_chrome_executable()
            
            # Start Chrome as a detached process
            chrome_cmd = [
                chrome_executable,
                f"--remote-debugging-port={self.port}",
                f"--user-data-dir={user_data_dir}",
                "--no-first-run",
                "--no-default-browser-check",
                "--start-maximized"
            ]
            
            print(f"Starting new Chrome instance with command: {' '.join(chrome_cmd)}")
            
            if os.name == 'nt':  # Windows
                process = subprocess.Popen(chrome_cmd, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
            else:  # Unix/Linux/MacOS
                process = subprocess.Popen(chrome_cmd, preexec_fn=os.setpgrp, start_new_session=True)
            
            # Store PID and port
            with open(self.pid_file, 'w') as f:
                f.write(str(process.pid))
            with open(self.port_file, 'w') as f:
                f.write(str(self.port))
                
            print(f"Started new Chrome instance with PID: {process.pid}, port: {self.port}")
            
            # Give Chrome some time to start up
            time.sleep(3)
            
            # Connect to the browser
            options = Options()
            options.add_experimental_option("debuggerAddress", f"127.0.0.1:{self.port}")
            self.browser = webdriver.Chrome(options=options)
            
            print("Connected to new Chrome instance")
            return True
            
        except Exception as e:
            print(f"Error starting new browser: {e}")
            return False
    
    def _find_chrome_executable(self):
        """Find the Chrome executable path based on OS"""
        if os.name == 'nt':  # Windows
            import winreg
            try:
                # Try to get from registry
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe")
                chrome_path, _ = winreg.QueryValueEx(key, None)
                return chrome_path
            except:
                # Fallback to common locations
                common_locations = [
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
                ]
                for location in common_locations:
                    if os.path.exists(location):
                        return location
                return "chrome.exe"  # Hope it's in PATH
        elif os.name == 'posix':  # Linux/Mac
            # Try common locations
            common_locations = [
                "/usr/bin/google-chrome",
                "/usr/bin/chromium-browser",
                "/usr/bin/chromium",
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"  # Mac
            ]
            for location in common_locations:
                if os.path.exists(location):
                    return location
            return "google-chrome"  # Hope it's in PATH
        else:
            return "google-chrome"  # Default
    
    def _find_available_port(self, start_port=9222, max_port=9322):
        """Find an available port for Chrome remote debugging"""
        import socket
        
        for port in range(start_port, max_port):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if s.connect_ex(('localhost', port)) != 0:
                    return port
                    
        # Fallback to default if no port is available
        return start_port
    
    def initialize(self):
        """Initialize the browser - connect to existing one or start a new one"""
        if self.is_browser_running() and self.connect_to_existing_browser():
            # Check if we're already logged in
            if not self.is_logged_in():
                self.login()
        else:
            self.start_new_browser()
            self.login()
        
        return self.browser is not None
        
    def is_logged_in(self):
        """Check if we're logged into Twitter"""
        try:
            self.browser.get("https://twitter.com/home")
            time.sleep(3)  # Give page time to load
            
            # If we see the login button, we're not logged in
            login_buttons = self.browser.find_elements(By.XPATH, "//a[@href='/login']")
            return len(login_buttons) == 0
        except Exception as e:
            print(f"Error checking login status: {e}")
            return False
    
    def login(self):
        """Log into Twitter with credentials from env vars"""
        try:
            print("Logging into Twitter...")
            self.browser.get("https://twitter.com/login")
            time.sleep(3)  # Wait for page to load
            
            # Enter username
            username_field = WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@autocomplete='username']"))
            )
            username_field.send_keys(self.username)
            
            # Click Next
            next_button = WebDriverWait(self.browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']"))
            )
            next_button.click()
            time.sleep(2)
            
            # Enter password
            password_field = WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@name='password']"))
            )
            password_field.send_keys(self.password)
            
            # Click Login
            login_button = WebDriverWait(self.browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[text()='Log in']"))
            )
            login_button.click()
            
            # Wait for login to complete
            WebDriverWait(self.browser, 20).until(
                EC.presence_of_element_located((By.XPATH, "//div[@data-testid='primaryColumn']"))
            )
            print("Successfully logged into Twitter")
            
        except Exception as e:
            print(f"Login failed: {e}")
            raise
    
    def get_profile_tweets(self, count=20):
        """Navigate to user's profile and collect tweet data"""
        try:
            # Navigate to user's profile
            self.browser.get(f"https://twitter.com/{self.username}")
            time.sleep(3)
            
            tweets = []
            tweet_elements = []
            last_height = self.browser.execute_script("return document.body.scrollHeight")
            
            # Keep scrolling until we have enough tweets or can't find more
            while len(tweets) < count:
                # Find tweet elements
                new_elements = self.browser.find_elements(By.XPATH, "//article[@data-testid='tweet']")
                
                # Filter out elements we've already processed
                new_elements = [elem for elem in new_elements if elem not in tweet_elements]
                tweet_elements.extend(new_elements)
                
                for elem in new_elements:
                    try:
                        # Check if it's a retweet (we want to skip these)
                        retweet_indicators = elem.find_elements(By.XPATH, ".//span[contains(text(), 'Retweeted')]")
                        if retweet_indicators:
                            continue
                        
                        # Check if it's an ad
                        ad_indicators = elem.find_elements(By.XPATH, ".//span[contains(text(), 'Ad')]")
                        if ad_indicators:
                            continue
                        
                        # Get the tweet URL from the timestamp element
                        timestamp = elem.find_element(By.XPATH, ".//time")
                        tweet_url = timestamp.find_element(By.XPATH, "./..").get_attribute("href")
                        
                        tweets.append({
                            "element": elem,
                            "url": tweet_url
                        })
                        
                        if len(tweets) >= count:
                            break
                    except Exception as e:
                        print(f"Error processing tweet: {e}")
                
                # Scroll down
                self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                # Check if we've reached the end of the page
                new_height = self.browser.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            
            return tweets[:count]
            
        except Exception as e:
            print(f"Error getting profile tweets: {e}")
            return []
    
    def get_tweet_engagements(self, tweet_url):
        """Get engagement data for a specific tweet"""
        try:
            # Navigate to the tweet
            self.browser.get(tweet_url)
            time.sleep(3)
            
            # Click on Post Engagements
            engagements_button = WebDriverWait(self.browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='More']"))
            )
            engagements_button.click()
            time.sleep(1)
            
            post_engagements = WebDriverWait(self.browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Post engagements')]"))
            )
            post_engagements.click()
            time.sleep(2)
            
            # Collect engagement data
            engagements = {
                "likes": self.get_user_list("Liked by"),
                "retweets": self.get_user_list("Reposted by"),
                "quotes": self.get_user_list("Quoted"),
            }
            
            # Go back to the tweet to collect replies
            self.browser.get(tweet_url)
            time.sleep(2)
            engagements["replies"] = self.get_replies()
            
            return engagements
            
        except Exception as e:
            print(f"Error getting engagements for tweet {tweet_url}: {e}")
            return {"likes": [], "retweets": [], "quotes": [], "replies": []}
    
    def get_user_list(self, tab_name):
        """Get list of users from a specific engagement tab"""
        users = []
        try:
            # Find and click the tab
            tab = WebDriverWait(self.browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"//span[contains(text(), '{tab_name}')]"))
            )
            tab.click()
            time.sleep(2)
            
            last_height = 0
            scrolls = 0
            max_scrolls = 10  # Limit scrolling to avoid infinite loops
            
            while scrolls < max_scrolls:
                # Get all user elements
                user_elements = self.browser.find_elements(By.XPATH, "//div[@data-testid='cellInnerDiv']//a[contains(@href, '/')]")
                
                for elem in user_elements:
                    try:
                        # Extract username from href
                        href = elem.get_attribute("href")
                        if href and "/status/" not in href:
                            username = href.split('/')[-1]
                            if username and username not in users:
                                users.append(username)
                    except:
                        continue
                
                # Scroll down
                self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                # Check if we've reached the end
                new_height = self.browser.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                scrolls += 1
                
        except Exception as e:
            print(f"Error getting users for {tab_name}: {e}")
            
        return users
    
    def get_replies(self):
        """Get usernames of accounts that replied to the tweet"""
        replies = []
        try:
            # Scroll down to load replies
            for _ in range(3):  # Scroll a few times to load more replies
                self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            # Find reply elements
            reply_elements = self.browser.find_elements(By.XPATH, "//article[@data-testid='tweet']")
            
            # Skip the first one as it's the original tweet
            for elem in reply_elements[1:]:
                try:
                    # Get username element
                    username_elem = elem.find_element(By.XPATH, ".//div[@data-testid='User-Name']//a")
                    username = username_elem.get_attribute("href").split('/')[-1]
                    
                    # Check if it's an ad
                    ad_indicators = elem.find_elements(By.XPATH, ".//span[contains(text(), 'Ad')]")
                    if not ad_indicators and username not in replies:
                        replies.append(username)
                except:
                    continue
                    
        except Exception as e:
            print(f"Error getting replies: {e}")
            
        return replies
    
    def get_list_members(self, list_url):
        """Get members of a Twitter list"""
        try:
            self.browser.get(list_url)
            time.sleep(3)
            
            # Wait for and click on "List members" to see the popup
            members_button = WebDriverWait(self.browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'List members')]"))
            )
            members_button.click()
            time.sleep(2)
            
            members = []
            last_height = 0
            scrolls = 0
            max_scrolls = 10  # Limit scrolling to avoid infinite loops
            
            # Locate the popup dialog
            popup = WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']"))
            )
            
            while scrolls < max_scrolls:
                # Get all user elements in the popup
                user_elements = popup.find_elements(By.XPATH, ".//div[@data-testid='cellInnerDiv']//a[contains(@href, '/')]")
                
                for elem in user_elements:
                    try:
                        # Extract username from href
                        href = elem.get_attribute("href")
                        if href and "/status/" not in href:
                            username = href.split('/')[-1]
                            if username and username not in members:
                                members.append(username)
                    except:
                        continue
                
                # Scroll down in the popup
                self.browser.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", popup)
                time.sleep(2)
                
                # Check if we've reached the end
                new_height = self.browser.execute_script("return arguments[0].scrollHeight", popup)
                if new_height == last_height:
                    break
                last_height = new_height
                scrolls += 1
                
            return members
            
        except Exception as e:
            print(f"Error getting list members: {e}")
            return []

    def close(self):
        """Disconnect from the browser without closing it"""
        if self.browser:
            self.browser.quit()  # This will only quit the WebDriver, not the Chrome instance