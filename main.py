from bs4 import BeautifulSoup
from urllib.request import urlopen
from pathlib import Path
import os
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
import requests
import time

### This File serves as a web scraper for https://soundgasm.net
### It downloads files by author. 
### Enter author's username as seen in URl to download their entire portfolio.

### Once download starts, a new folder with the author's username is created.
### Inside that folder all the files are downloaded.


DOWNLOAD_CHUNKSIZE = 8192 

BETWEEN_DOWNLOADS_DELAY = 2 # The delay between each download in seconds. Adjust to your internet speed
HEADLESS = False # UI toggle. Set to true to see every action. Set to false to have it work in the background
ASK_BEFORE_DOWNLOAD = False # Won't work without UI

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))

class Scraper():

    def __init__(self):
        self.TOTAL_FILES = 0
        self.SUCCESSFUL_FILES = 0
        self.FILENAMES = []

        self.username = self.GetUsername()
        self.InitializeDirectory()
        self.InitializeWebDriver()
        
        url = "https://soundgasm.net/u/" + self.username
        content = self.GetContentList(url)
        self.ParseContent(content)

    # Create a directory with the author's username
    def InitializeDirectory(self):
        if not os.path.exists(self.username):
            os.mkdir(self.username)


    # Create self.driver object
    def InitializeWebDriver(self):
        options = Options()

        download_folder = os.path.join(SCRIPT_PATH, self.username)

        firefox_path = os.path.join(SCRIPT_PATH, "firefox", "firefox-bin")
        geckodriver_path = os.path.join(SCRIPT_PATH, "geckodriver")

        profile = FirefoxProfile()
        profile.set_preference("browser.download.folderList", 2)
        profile.set_preference("browser.download.manager.showWhenStarting", ASK_BEFORE_DOWNLOAD)
        profile.set_preference("browser.download.dir", download_folder)
        profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "audio/mpeg, audio/x-wav, audio/mp4, application/octet-stream")

        options.headless = HEADLESS
        options.binary_location = firefox_path
        self.driver = webdriver.Firefox(service=Service(geckodriver_path), options=options)

    # Prompt user to enter author's username
    def GetUsername(self):
        username = None

        while (type(username) != str):
            username = str(input("Enter the author\'s username > "))

        return username

    # Scrape the author's portfolio for content
    def GetContentList(self, url):
        response = urlopen(url)
        content = response.read()
        decodedContent = content.decode('utf-8')

        return decodedContent

    # Parse through the retrieved content and extract titles and URl's
    def ParseContent(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        sound_details_divs = soup.find_all('div', class_='sound-details')
        self.TOTAL_FILES = len(sound_details_divs) - 1
        titleUrlPairs = {}


        for div in sound_details_divs:
            
            print("\nFound:")

            self.filename = div.a.get_text()
            self.download_path = os.path.join(self.username, self.filename)

            fileExists = os.path.exists(self.download_path)

            if not fileExists:

                url = div.a.get('href')
                print("filename: ", self.filename)
                sourceURl = self.ExtractDownloadUrl(url)
                self.DownloadFile(sourceURl)

            else:
                print("File already downloaded!")
                pass
            

    # Extract the embedded media URl
    def ExtractDownloadUrl(self,url):
        self.driver.get(url)
        time.sleep(BETWEEN_DOWNLOADS_DELAY)


        WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'jp-jplayer'))
            )

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "audio"))
        )

        content = self.driver.page_source
        soup = BeautifulSoup(content, 'html.parser')
        jplayerTag = soup.find("div", class_="jp-jplayer")
        audioTag = jplayerTag.find("audio")
        srcUrl = audioTag.get("src")
        print("URl: ", srcUrl)

        return srcUrl

    # Send a download request for the file and save it
    def DownloadFile(self, srcUrl):
        
        try:
            filename_with_extension = os.path.basename(srcUrl)
            _, self.extension = os.path.splitext(filename_with_extension)

            self.download_path = os.path.join(self.username, self.filename + self.extension)
            response = requests.get(srcUrl, stream=True)
            response.raise_for_status() 

            with open(self.download_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=DOWNLOAD_CHUNKSIZE):
                    file.write(chunk)

            print(f"Downloaded: {self.download_path}")
            self.SUCCESSFUL_FILES += 1
            self.FILENAMES.append(self.filename)

        except Exception as e:
            print(f"Error downloading file: {e}")


    # On exit, close browser
    def __del__(self):
        print("Finished!")

        if self.TOTAL_FILES < 0:
            print("removing ", os.path.join(SCRIPT_PATH, self.username))
            os.rmdir(os.path.join(SCRIPT_PATH, self.username))

        for filename in self.FILENAMES:
            print("+ ", filename)
        
        print("Total files downloaded: ", self.SUCCESSFUL_FILES, " / ", self.TOTAL_FILES)
        if hasattr(self, 'driver'):
            self.driver.quit()


if __name__ == "__main__":
    scraper = Scraper()