from selenium.webdriver import Chrome
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
from typing import Dict, List, Tuple
import os
import urllib

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

    class Result:
        '''
        Inner class for storing the results of scraping data from a webpage.
        '''
        def __init__(self, driver: Chrome, fetch_strategies: Tuple[Tuple[str]]) -> None:
            self.__driver = driver
            self.__fetch_strategies = {

            }
        

        def from_pages(self, urls: List[str]) -> Dict[str, str]:
            '''
            Fetches data at each given URL.

            Parameters
            ----------
            urls: List[str]
                List of URLs to scrape.
            
            Returns
            -------
            Dict[str, str] : SQL-ready dictionary containing scraped data.
            '''

            data = {
                f[0]: [] for f in self.__fetch_strategies
            }

            data['uuid'] = uuid4()

            for url in urls:
                self.__driver.get(url)

                for f in self.__fetch_strategies:
                    try:
                        fetch_data = self.__driver.find_element(f[1], f[2]).get_attribute(self.__attribute)
                    except:
                        fetch_data = ''
                    
                    data[f[0]].append(fetch_data)
            
            return data
    
    
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