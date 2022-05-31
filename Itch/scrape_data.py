from selenium.common.exceptions import NoSuchElementException
from typing import Dict, List
from uuid import uuid4
import json
import os
import scraper

class ScrapeData:
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
            scraper: scraper.Scraper,
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
            perform_dump: bool=True) -> Dict:
        '''
        Fetches data at each given URL.

        ### Parameters
        `urls: List[str]`
            List of URLs to scrape.
        
        `perform_dump: bool`
            If set to False, do not automatically dump data after scraping. (Default: True)
        
        ### Returns
        `Dict[str, str]` : SQL-ready dictionary containing scraped data.
        '''

        print('\nScraping...')

        for url in urls:
            print()

            self.__get(url)
            
            print('Creating UUID4...')
            uuid = uuid4().urn
            self.__data['uuid'].append(uuid)

            for column_name, locator in self.__locators.items():
                by, value, html_attribute = locator.by, locator.value, locator.html_attribute

                try:
                    print(f'Scraping field \'{column_name}\'...')
                    row_data = self.__find_element(by, value).get_attribute(html_attribute)

                except NoSuchElementException:
                    print(f'ERROR: Could not find element with {by} \'{value}\'.')
                
                if row_data is None:
                    print(f'ERROR: Element does not have attribute or property with name "{html_attribute}".')
                    row_data = locator.default_if_not_found

                print(f'Appending data...')

                self.__data[column_name].append(row_data)
        
        print(f'\nScraping complete.')

        if perform_dump:
            self.dump()

        return self.__data
    

    def dump(self,
            dir: str='./raw_data/',
            filename: str='data.json') -> None:
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
        
        print('\nPerforming JSON dump...')

        try:
            with open(filepath, 'w') as file:
                json.dump(self.__data, file)
            print('Dump complete.')
        
        except Exception as e:
            print('ERROR: Could not perform dump.')
            print(e)