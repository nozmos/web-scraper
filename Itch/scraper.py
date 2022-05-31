from __future__ import annotations
from locator import Locator, LOCATE
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
from typing import Any, Callable, Dict, List, Tuple
from webdriver_manager.chrome import ChromeDriverManager
import os
import scraping_method
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


    # DECORATORS
    def __log_url(func: Callable) -> Callable:

        def wrapper(self: Scraper, *args, **kwargs) -> Any:

            result = func(self, *args, **kwargs)

            print(f'[{self.__driver.current_url}]')

            return result
            
        return wrapper


    # PROPERTIES
    @property
    def current_url(self) -> str:
        return self.__driver.current_url

    
    # INSTANCE METHODS
    @__log_url
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
    

    @__log_url
    def home(self) -> None:
        '''
        Load the scraper object's root URL.
        '''
        self.__driver.get(self.__root)
    

    @__log_url
    def get(self, url: str) -> None:
        '''
        Loads a webpage in the current browser session.
        '''
        self.__driver.get(url)
    

    @__log_url
    def back(self) -> None:
        '''
        Goes one step backward in the user's history.
        '''
        self.__driver.back()
    

    @__log_url
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


    @__log_url
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
    

    def retrieve_urls(self,
            by: str,
            value: str,
            limit: int=None,
            next_button_xpath: str=None) -> List[str]:
        '''
        Retrieves a list of URLs from the href attribute of the given elements on the current webpage.

        ### Parameters
        `by: str`
            Strategy for locating elements.
        
        `value: str`
            Value by which to search according to the locator strategy.
        
        `limit: int`
            Max number of results to fetch. If None, obtain all results possible. (Default: None)

        `next_button_xpath: str`
            XPath to the "Next" button (if applicable) to allow searching of multiple pages. (Default: None)
        
        ### Returns
        `List[str]` : List of URLs from the href property of each selected element.
        '''

        elements = []
        response = 'Finished retrieving URLs.'

        print(f'Retrieving URLs from {self.__driver.current_url}')
        print(f'Using {by} \'{value}\'')

        if limit:
            print(f'Limit: {limit}')
            while len(elements) < limit:
                elements.extend(self.find_elements(by, value))
            elements = elements[:limit]

        elif next_button_xpath:
            while True:
                try:
                    next_button = self.find_element(By.XPATH, next_button_xpath)
                except:
                    print(f'Could not find next_button at XPATH \'{next_button_xpath}\'')
                    response = 'URL retrieval interrupted. Terminating...'
                    break

                elements.extend(self.find_elements(by, value))
                next_button.click()
        
        else:
            elements = self.find_elements(by, value)
        
        print(response)

        return list(element.get_attribute('href') for element in elements)


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
    

    def create_scraping_method(self, **locators: Locator | Tuple) -> scraping_method.ScrapingMethod:
        '''
        Prepares a ScrapeData object which can retrieve data from given webpages.

        It is recommended to use `locate()` for defining locators, to increase readability (see below).

        ### Parameters
        `**locators: Locator | Tuple`
            Keyword arguments for locators.

        ### Usage
        ```python
        get_product_name_and_price = scraper.create_scraping_method(
            product_name = LOCATE.TEXT.BY.CLASS_NAME('product-title')
            price = LOCATE.TEXT.BY.CSS_SELECTOR('h2.price-tag')
        )
        
        data = get_product_name_and_price.from_pages(
            ['http://www.mywebsite.com/products/1', 'http://www.mywebsite.com/products/2']
        )
        ```
        `from_pages()` is an instance method of the `ScrapeData` class for performing the scrape on a list of URLs.
        The `from_pages()` instance method will automatically perform a JSON dump of all fetched data into a local directory unless `perform_dump` is set to False.

        Dumped data will be in the following SQL-ready form (using the above as an example):
        ```JSON
        {
            "product_name": ["HB Pencil", "A4 Notepad"],
            "price": ["£0.99", "£2.99"],
            "uuid": ["urn:uuid:9954bc7f-937b-4519-b1e6-ee1b39b07deb", "urn:uuid:8e726fb4-04f1-485a-aaa0-b46f42096e1d"]
        }
        ```
        '''
        # If tuples are used, convert to Locator objects
        for id, locator_like in locators.items():
            if isinstance(locator_like, Tuple):

                if len(locator_like) == 2:
                    html_attribute = 'textContent'
                    strategy = locator_like[0]
                    value = locator_like[1]
                    locators[id] = LOCATE.html_attribute(html_attribute).by(strategy)(value)
                
                elif len(locator_like) == 3:
                    html_attribute = locator_like[0]
                    strategy = locator_like[1]
                    value = locator_like[2]
                    locators[id] = LOCATE.html_attribute(html_attribute).by(strategy)(value)
        
        return scraping_method.ScrapingMethod(self, locators)