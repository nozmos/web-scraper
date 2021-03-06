from __future__ import annotations
from locator import Locator, LOCATE, LocatorNotDefinedError
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
from typing import Any, Callable, Dict, List, Tuple
from uuid import uuid4
from webdriver_manager.chrome import ChromeDriverManager
import boto3
import json
import os
import time
import urllib


class ScrapingMethod:
    '''
    Object class for holding scraping strategies for later execution, and storing the results.

    ### Properties
    `__find_element: Callable`
        `find_element` function of the Scraper object passed on initalisation.
    
    `__get: Callable`
        `get` function of the Scraper object passed on initalisation.
    
    `__locators: Dict`
        Dictionary of data column names with their associated Locators.

    `__data: Dict`
        Contains scraped data and associated UUIDs.
    '''
    
    def __init__(self,
            scraper: Scraper,
            locators: Dict) -> None:
        '''
        Initialises the ScrapeData Object.

        ### Parameters
        `scraper: Scraper`
            Scraper object to be used.
        
        `locators: Dict`
            Dictionary of data column names with their associated Locators.
        '''

        print('\nPreparing ScrapeData object...')

        self.__find_element = scraper.find_element
        self.__get = scraper.get
        self.__locators = locators
            

        # Initialise data dict using keys from locator dictionary
        self.__data = { column_name: [] for column_name in self.__locators.keys() if column_name != 'uuid' }
        
        self.__data['uuid'] = []
    

    def from_pages(self,
            urls: List[str],
            dump_json: bool=True,
            s3_bucket_name: str=None,
            sleep_time: int=2) -> Dict:
        '''
        Fetches data at each given URL.

        ### Parameters
        `urls: List[str]`
            List of URLs to scrape.
        
        `dump_json: bool`
            If set to False, do not automatically dump data after scraping. (Default: True)
        
        ### Returns
        `Dict[str, str]` : SQL-ready dictionary containing scraped data.
        '''

        print('\nScraping...')

        urls = list(set(urls)) # Prevent re-scraping the same page.

        for url in urls:
            print()

            self.__get(url)
            time.sleep(sleep_time)
            
            print('Creating UUID4...')
            uuid = uuid4().urn
            self.__data['uuid'].append(uuid)

            for column_name, locator in self.__locators.items():
                by, value, html_attribute, convert_to_type = locator.by, locator.value, locator.html_attribute, locator.convert_to_type
                row_data = None

                try:
                    print(f'Scraping field \'{column_name}\'...')
                    row_data = self.__find_element(by, value).get_attribute(html_attribute)

                except NoSuchElementException:
                    print(f'ERROR: Could not find element with {by} \'{value}\'.')
                
                if row_data is None:
                    print(f'ERROR: Element does not have attribute or property with name "{html_attribute}".')
                    row_data = locator.default_if_not_found
                
                elif convert_to_type is not None:
                    try:
                        row_data = convert_to_type(row_data)
                    except:
                        print(f'Failed to convert row data to type "{convert_to_type}".')

                print(f'Appending data...')

                self.__data[column_name].append(row_data)
        
        print(f'\nScraping complete.')

        if dump_json:
            self.dump(s3_bucket_name=s3_bucket_name)

        return self.__data
    

    def dump(self,
            dir: str='./raw_data/',
            filename: str='data.json',
            s3_bucket_name: str=None) -> None:
        '''
        Creates a new directory (if one doesn't exist), and performs a JSON dump of currently stored data.

        ### Parameters
        `dir: str`
            Path for the directory where data will be dumped. (Default: './raw_data/')
        
        `filename: str`
            Name of the file in which to dump data. (Default: 'data.json')
        '''

        print(f'Creating directory at {dir}')

        os.makedirs(dir, exist_ok=True)
        filepath = os.path.join(dir, filename)
        print(filepath)
        
        print('\nPerforming JSON dump...')

        try:
            with open(filepath, 'w') as file:
                json.dump(self.__data, file)

            if s3_bucket_name is not None:
                print('Creating s3 client...')
                s3_client = boto3.client('s3')

                print(f'Uploading to S3 bucket "{s3_bucket_name}" from filepath "{filepath}"...')
                response = s3_client.upload_file(filepath, s3_bucket_name, filename)

                print('Finished uploading.')

            print('Dump complete.')
        
        except Exception as e:
            print('ERROR: Could not perform dump.')
            print(e)


class Scraper:
    '''
    Webscraping class for automatically retrieving data from webpages.

    ### Properties
    `driver: WebDriver`
        Main driver for the class. Handles requests and data retrieval.
    
    `root: str`
        Root URL. Can be loaded with the Scraper.home() method. May be modified using the set_root method.
    '''
    
    def __init__(self,
            root: str,
            headless: bool=False,
            ignore_warnings: bool=True,
            s3_bucket_name: str=None) -> None:
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

        options.add_argument('--disable-dev-shm-usage')

        if ignore_warnings:
            options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
            options.set_capability('detach', True)
        
        if headless:
            options.add_argument('--headless')
        
        # initialise driver and load root URL
        self.__driver = Chrome(ChromeDriverManager().install(), options=options)

        self.__root = root
        self.__s3_bucket_name = s3_bucket_name

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

        ### Parameters
        `URL: str`
            New URL to replace the current one.
        '''
        self.__root = url
    

    def quit(self) -> None:
        '''
        Quits the driver and closes every associated window.
        '''
        self.__driver.quit()
    

    def find_element(self, by: str | Locator, value: str) -> WebElement:
        '''
        Find an element given a By strategy and locator.

        ### Parameters
        `by: str | Locator`
            Strategy for locating elements.
        
        `value: str`
            Value by which to search according to the locator strategy.
        '''

        if isinstance(by, str):
            if value is None:
                raise LocatorNotDefinedError(f'{by} not defined.')
            
        elif isinstance(by, Locator):
            _locator = by
            by = _locator.by
            value = _locator.value
        
        return self.__driver.find_element(by, value)
    
    
    def find_elements(self, by: str | Locator, value: str) -> List[WebElement]:
        '''
        Find elements given a By strategy and locator.

        ### Parameters
        `by: str | Locator`
            Strategy for locating elements.
        
        `value: str`
            Value by which to search according to the locator strategy.
        '''

        if isinstance(by, str):
            if value is None:
                raise LocatorNotDefinedError(f'{by} not defined.')
            
        elif isinstance(by, Locator):
            _locator = by
            by = _locator.by
            value = _locator.value
        
        result = self.__driver.find_elements(by, value)

        if not result:
            print(f'Could not find element using {by} "{value}".')
        
        return result


    @__log_url
    def click_element(self, by: str | Locator, value: str=None) -> None:
        '''
        Finds an element and clicks on it.

        ### Parameters
        `by: str | Locator`
            Strategy for locating elements.
        
        `value: str`
            Value by which to search according to the locator strategy.
        '''

        if isinstance(by, str):
            if value is None:
                raise LocatorNotDefinedError(f'{by} not defined.')
            
        elif isinstance(by, Locator):
            _locator = by
            by = _locator.by
            value = _locator.value
        
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

        ### Parameters
        `height: int`
            Height to scroll to (in pixels). 0 is the top of the document.
        '''
        self.__driver.execute_script(f'window.scrollTo({height});')
    

    def retrieve_urls(self,
            by: str | Locator,
            value: str=None,
            limit: int=None,
            next_button_xpath: str=None) -> List[str]:
        '''
        Retrieves a list of URLs from the href attribute of the given elements on the current webpage.

        ### Parameters
        `by: str | Locator`
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

        if isinstance(by, str):
            if value is None:
                raise LocatorNotDefinedError(f'{by} not defined.')
            
        elif isinstance(by, Locator):
            _locator = by
            by = _locator.by
            value = _locator.value

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

        ### Parameters
        `extensions: str`
            List of URL extensions to append.
        '''

        new_url = self.__driver.current_url.removesuffix('/')
        for extension in extensions:
            new_url += '/' + extension
        
        self.__driver.get(new_url)


    def trim_url(self, *extensions: str) -> None:
        '''
        Removes extensions from the current URL, then gets the new URL.

        ### Parameters
        `extensions: str`
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
    

    def create_scraping_method(self, **locators: Locator | Tuple) -> ScrapingMethod:
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
            "price": ["??0.99", "??2.99"],
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
        
        return ScrapingMethod(self, locators)