from __future__ import annotations
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
from typing import Dict, List, Tuple
from webdriver_manager.chrome import ChromeDriverManager
import os
import scrape_data
import urllib


class Scraper:
    '''
    Webscraping class for automatically retrieving data from webpages.

    ### Properties
    driver: WebDriver
        Main driver for the class. Handles requests and data retrieval.
    
    root: str
        Root URL. Can be loaded with the Scraper.home() method. May be modified using the set_root method.
    '''
    
    def __init__(self,
            root: str,
            headless: bool=False,
            ignore_warnings: bool=True) -> None:
        '''
        Initialises the Scraper object.

        ### Parameters
        `root: str`
            Root URL of the webpage to be scraped. Get request is sent on initialisation.
        
        `headless: bool`
            Tells the scraper whether or not to initialise in headless mode. (Default: False)
        
        `ignore_warnings: bool`
            Ignores warnings that can occur on Windows when Python attempts to start a Selenium driver. (Default: False)
        '''

        options = Options()

        if ignore_warnings:
            options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
            options.set_capability('detach', True)
        
        if headless:
            options.add_argument('--headless')
        
        # initialise driver and load root URL
        self.__driver = Chrome(ChromeDriverManager().install(), options=options)

        self.__root = root

        self.home()


    # PROPERTIES
    @property
    def current_url(self) -> str:
        return self.__driver.current_url

    
    # INSTANCE METHODS
    def search(self,
            search_terms: str,
            input_xpath: str='//input[@class="search_input"]',
            button_xpath: str='//button[@aria-label="Search"]') -> None:
        '''
        Performs a search using the search bar on the current webpage.

        ### Parameters
        `search_terms: str`
            String which will be used for the search.
        
        `input_xpath: str`
            XPath to the search bar input element. (Default: '//input[@class="search_input"]')
        
        `button_xpath: str`
            XPath to the search button element. (Default: '//button[@aria-label="Search"]')
        '''

        print('Attempting search...')
        
        try:
            search_bar = self.__driver.find_element(By.XPATH, input_xpath)
        except:
            print(f'Unable to find search bar with XPATH \'{input_xpath}\'. Terminating search...')
            return
        
        try:
            search_button = self.__driver.find_element(By.XPATH, button_xpath)
        except:
            print(f'Unable to find search button with XPATH \'{button_xpath}\'. Terminating search...')
            return
        
        try:
            search_bar.send_keys(search_terms)
            search_button.click()
        except Exception as e:
            print(f'Could not perform search.')
            print(e)
            return
    

    def home(self) -> None:
        '''
        Load the scraper object's root URL.
        '''
        self.__driver.get(self.__root)
    

    def get(self, url: str) -> None:
        '''
        Loads a webpage in the current browser session.
        '''
        self.__driver.get(url)
    

    def back(self) -> None:
        '''
        Goes one step backward in the user's history.
        '''
        self.__driver.back()
    

    def forward(self) -> None:
        '''
        Goes one step forward in the user's history.
        '''
        self.__driver.forward()
    

    def set_root(self, url: str) -> None:
        '''
        Sets the scraper object's root URL.

        Parameters
        ----------
        URL: str
            New URL to replace the current one.
        '''
        self.__root = url
    

    def quit(self) -> None:
        '''
        Quits the driver and closes every associated window.
        '''
        self.__driver.quit()
    

    def find_element(self, by: str, value: str) -> WebElement:
        '''
        Find an element given a By strategy and locator.

        Parameters
        ----------
        by: str
            Strategy for locating elements.
        
        value: str
            Value by which to search according to the locator strategy.
        '''
        return self.__driver.find_element(by, value)
    
    
    def find_elements(self, by: str, value: str) -> List[WebElement]:
        '''
        Find elements given a By strategy and locator.

        Parameters
        ----------
        by: str
            Strategy for locating elements.
        
        value: str
            Value by which to search according to the locator strategy.
        '''
        return self.__driver.find_elements(by, value)


    def click_element(self, by: str, value: str) -> None:
        '''
        Finds an element and clicks on it.

        Parameters
        ----------
        by: str
            Strategy for locating elements.
        
        value: str
            Value by which to search according to the locator strategy.
        '''
        element = self.__driver.find_element(by, value)
        element.click()


    def scroll_to_bottom(self) -> None:
        '''
        Scrolls to the bottom of the current page.
        '''
        self.__driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    

    def scroll_to(self, height: int) -> None:
        '''
        Scrolls to a specified point on the page, in pixels.

        Parameters
        ----------
        height: int
            Height to scroll to (in pixels). 0 is the top of the document.
        '''
        self.__driver.execute_script(f'window.scrollTo({height});')


    def extend_url(self, *extensions: str) -> None:
        '''
        Appends to the current URL, separating by forward-slashes, then gets the new URL.

        Parameters
        ----------
        extensions: str
            List of URL extensions to append.
        '''

        new_url = self.__driver.current_url.removesuffix('/')
        for extension in extensions:
            new_url += '/' + extension
        
        self.__driver.get(new_url)


    def trim_url(self, *extensions: str) -> None:
        '''
        Removes extensions from the current URL, then gets the new URL.

        Parameters
        ----------
        extensions: str
            Strings to remove from current URL, including leading forward-slashes.
        '''

        new_url = self.__driver.current_url
        for extension in extensions:
            new_url = new_url.replace('/' + extension + '/', '/')
        
        self.__driver.get(new_url)


    def download_image(self, url: str, filename: str) -> None:
        '''
        Download the image stored at the given url in a list, and temporarily store it under a local directory with the given filename.

        ### Parameters
        `url: str`
            URL of image.
        
        `filename: str`
            File name to save the image under (extension included).
        '''
        os.makedirs('./raw_data/images/', exist_ok=True)

        urllib.request.urlretrieve(url, os.path.join('./raw_data/images/', filename))
    

    def download_images(self, url_list: List[str]) -> None:
        '''
        Downloads the images stored at each url in a list and temporarily stores them in a local directory.

        ### Parameters
        `url_list: List[str]`
            List of image URLs.
        '''
        for _index, _url in enumerate(url_list):
            file_extension = _url.rpartition('.')[-1]
            self.download_image(_url, f'image{_index}.{file_extension}')