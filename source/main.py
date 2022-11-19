from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from dateutil import parser
import time
import requests
import pandas as pd
import dateutil.parser

# Function to check robots.txt file of the website
def get_robot_txt(url):
    if url.endswith('/'):
        path = url
    else:
        path = url + '/'
    req = requests.get(path + "robots.txt", data=None)
    return req.text

# Read the robots.txt of the web
print(get_robot_txt('https://twitter.com'))

class SeleniumClient(object):
    def __init__(self):
        '''
        Initialization function. Setting options for the webdriver
        '''
        self.chrome_options = webdriver.ChromeOptions()
        # self.chrome_options.add_argument('--headless')  # runs browser in headless mode
        self.chrome_options.add_argument(" — incognito")  # open incognito mode
        self.chrome_options.add_argument('--user-agent="Mozilla/5.0 (Windows Phone 10.0; Android 4.2.1; Microsoft; Lumia 640 XL LTE) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Mobile Safari/537.36 Edge/12.10166"')  # set our UserAgent name
        # Provide the path of chromdriver in your system
        # self.browser = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver") #Diego at home
        self.browser = webdriver.Chrome("/usr/bin/chromedriver")  #Diego at work
        # self.browser = webdriver.Chrome("C:/Users/albac/Downloads/chromedriver_win32/chromedriver") #Alba

        self.base_url = 'https://twitter.com/search?q='
        self.find_total = 100

    def format_numeric(self, data):
        '''
        Function to format "mil" data
        '''
        if ( len(data) == 0):
            data = '0'
        return data.replace(" mil", "000").replace(",", "").replace(".", "")

    def check_tweet(self, tweets, datetime):
        '''
        Function to check if a tweet is contained in list array.
        '''
        exist = False

        for tweet in tweets:
            if tweet[0] == datetime:
                exist = True
                break
        return exist

    def get_tweets(self, query):
        '''
        Function to get tweets.
        '''
        tweets = []  # Lists to capture data and images

        self.browser.get(self.base_url + query)  # get content from the website
        time.sleep(1)

        # Checking User-Agent
        agent = self.browser.execute_script("return navigator.userAgent")
        body = self.browser.find_element(By.TAG_NAME, "body")

        for _ in range(self.find_total):
            body.send_keys(Keys.PAGE_DOWN)
            time.sleep(1)  # Waitting for Javascript results

            # Manage logins and cookies(session)
            session = requests.Session()
            session.post("https://twitter.com/login", data=dict(
                email="me@domain.com",
                password="secret_value"
            ))
            # <!-- requests with sessions (cookies) -->
            r = session.get("https://twitter.com/protected_page")

            # Search for tweets
            all_tweets = self.browser.find_elements(By.XPATH, '//div[@data-testid]//article[@data-testid="tweet"]')

            # Data scraping
            for item in all_tweets[1:]:
                try:
                    image = item.find_element(By.XPATH, ".//img[contains(@src,'/media/')]").get_attribute("src")
                except:
                    image = ''
                try:
                    dateiso = item.find_element(By.XPATH, './/time').get_attribute("datetime")
                    datetime = dateutil.parser.parse(dateiso).strftime("%d/%m/%Y %H:%M:%S")
                except:
                    datetime = ''
                try:
                    text = item.find_element(By.XPATH, './/div[@data-testid="tweetText"]').text.strip().replace('\n','')
                except:
                    text = ''
                try:
                    reply = item.find_element(By.XPATH,'.//div[@data-testid="reply"]').text.strip()
                except:
                    reply = ''
                try:
                    like = item.find_element(By.XPATH, './/div[@data-testid="like"]').text.strip()
                except:
                    like = ''
                try:
                    retweet = item.find_element(By.XPATH, './/div[@data-testid="retweet"]').text.strip()
                except:
                    retweet = ''

                if len(tweets) > 0:
                    if selenium_client.check_tweet(tweets, datetime) == False:
                        tweets.append([datetime, selenium_client.format_numeric(reply), text, selenium_client.format_numeric(like), selenium_client.format_numeric(retweet), image])
                else:
                    tweets.append([datetime, selenium_client.format_numeric(reply), text, selenium_client.format_numeric(like), selenium_client.format_numeric(retweet), image])

        # Save data in csv file and images in .jpg format in a folder
        df = pd.DataFrame(tweets, columns=['DateTime of Tweet', 'Replying to', 'Tweet', 'Likes', 'Retweet', 'Image'])
        df.to_csv('tweets_' + query + '.csv', index=False, encoding='utf-8')

find_exp = 'musk'
print('Started web scraping TWITTER...')
print('Creating client browser...')

selenium_client = SeleniumClient()
print('Searching Tweets for ...', find_exp)

tweets_df = selenium_client.get_tweets(find_exp)
print('Finished web scraping TWITTER...')