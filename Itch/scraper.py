from selenium.webdriver import Chrome
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
from typing import List

class Scraper:
    '''
    Webscraping class for automatically retrieving data from webpages.

    Properties
    ----------
    driver: WebDriver
        Main driver for the class. Handles requests and data retrieval.
    
    root: str
        Root URL. Can be loaded with the Scraper.home() method. May be modified using the set_root method.
    '''
    
    
    def __init__(self, root: str, headless: bool=False, ignore_warnings: bool=False) -> None:
        '''
        Initialises the Scraper object.

        Parameters
        ----------
        root: str
            Root URL of the webpage to be scraped. Get request is sent on initialisation.
        
        headless: bool (Optional)
            Tells the scraper whether or not to initialise in headless mode. (Default: False)
        
        ignore_warnings: bool (Optional)
            Ignores warnings that can occur on Windows when Python attempts to start a Selenium driver. (Default: False)
        '''

        options = Options()

        if ignore_warnings:
            options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging']) # ignore Windows errors
            options.set_capability('detach', True)
        
        if headless:
            options.add_argument('--headless')
        
        # initialise driver and load root URL
        self.__driver = Chrome(ChromeDriverManager().install(), options=options)

        self.__root = root

        self.home()
    

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