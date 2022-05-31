from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable


class LocatorNotDefinedError(Exception): pass


@dataclass(frozen=True)
class Locator:
    '''
    Dataclass for locator strategies to make code more readable.

    ### Properties
    `html_attribute: str`
        The name of the HTML attribute (or property) to be located.
    
    `by: str`
        Strategy for locating elements.
    
    `value: str`
        Value by which to search according to the locator strategy.

    `default_if_not_found: Any`
        Value to return if the scraper cannot find a match for the locator.
    '''
    html_attribute: str
    by: str
    value: str
    default_if_not_found: Any = None


@dataclass
class _LOCATE:
    '''
    Singleton Dataclass for quick Locator construction. Object instantiation not required, use the LOCATE constant instead.

    ### Usage
    To construct a Locator, define the desired HTML attribute, By strategy, and Value according to the following example.

    `LOCATE.TEXT.BY.CSS_SELECTOR('h2.title-txt')`

    This returns a Locator object which can (in this case) be used to fetch the `textContent` attribute of the element found via its CSS selector, using the value `h2.title-text`. Use in conjunction with `create_scraping_method` in `scraper.py` to define each field.
    
    Several common attributes and strategies come pre-packaged in the LOCATE Singleton. If the desired attribute is not implemented, use the corresponding function (lower snake case) to define them:

    `LOCATE.html_attribute('data-field').BY.ID('table021')`

    While there is functionality to also define custom By strategies, it is not recommended as these will not be supported by Selenium's `find_element` function.
    '''

    __html_attribute: str = None
    __by: str = None

    # MAGIC METHODS
    def __repr__(self) -> str:
        if self.__html_attribute is None:
            raise LocatorNotDefinedError('HTML attribute not defined.')

        elif self.__by is None:
            raise LocatorNotDefinedError(f'BY strategy not defined.')

        else:
            raise LocatorNotDefinedError(f'{self.__by} not defined.')


    # DECORATORS
    def __sets_html_attribute(html_attribute_name: str=None):

        def decorator(func: Callable):

            def wrapper(self) -> _HTML_ATTRIBUTE:
                return _HTML_ATTRIBUTE(
                    func.__name__.lower() if html_attribute_name is None
                    else html_attribute_name)

            return wrapper
        
        return decorator


    # INSTANCE METHODS
    def html_attribute(self, html_attribute_name: str) -> _HTML_ATTRIBUTE:
        return _HTML_ATTRIBUTE(html_attribute_name)


    # ELEMENT PROPERTY (for if the element itself needs to be located)
    @property
    @__sets_html_attribute()
    def ELEMENT(): ...


    # PROPERTIES (HTML ATTRIBUTES)
    @property
    @__sets_html_attribute()
    def ACTION(): ...
    
    @property
    @__sets_html_attribute()
    def CLASS(): ...
    
    @property
    @__sets_html_attribute()
    def CONTENT(): ...
    
    @property
    @__sets_html_attribute()
    def CONTROLS(): ...
    
    @property
    @__sets_html_attribute()
    def HREF(): ...
    
    @property
    @__sets_html_attribute()
    def ID(): ...
    
    @property
    @__sets_html_attribute()
    def LANG(): ...
    
    @property
    @__sets_html_attribute()
    def NAME(): ...
    
    @property
    @__sets_html_attribute()
    def MEDIA(): ...
    
    @property
    @__sets_html_attribute()
    def PROPERTY(): ...
    
    @property
    @__sets_html_attribute()
    def REL(): ...
    
    @property
    @__sets_html_attribute()
    def ROLE(): ...
    
    @property
    @__sets_html_attribute()
    def SRC(): ...
    
    @property
    @__sets_html_attribute()
    def STYLE(): ...

    @property
    @__sets_html_attribute('textContent')
    def TEXT(): ...
    
    @property
    @__sets_html_attribute()
    def TITLE(): ...
    
    @property
    @__sets_html_attribute()
    def TYPE(): ...


@dataclass
class _HTML_ATTRIBUTE:
    '''
    First intermediate Dataclass to ease readability of LOCATE Singleton.
    '''

    name: str

    # MAGIC METHODS
    def __repr__(self) -> str:
        raise LocatorNotDefinedError('Locator must be given a By strategy.')


    # INSTANCE METHODS
    def by(self, by: str) -> _BY:
        return _BY(self.name, by.replace('_', ' ').lower())


    # PROPERTIES
    @property
    def BY(self): return _BY(self.name)


@dataclass
class _BY:
    '''
    Second intermediate Dataclass to ease readability of LOCATE Singleton. Contains implementation for all By strategies currently supported by Selenium's `find_element` function.
    '''

    __html_attribute: str
    __by: str = None
    
    # MAGIC METHODS
    def __call__(self, value: str, default_if_not_found: Any=None) -> Locator:
        if self.__by is None:
            raise LocatorNotDefinedError('Locator must be given a By strategy.')

        else:
            return Locator(self.__html_attribute, self.__by, value, default_if_not_found)


    def __repr__(self) -> str:
        raise LocatorNotDefinedError('Locator must be given a By strategy.')


    # DECORATORS
    def __sets_by(func: Callable):
        
        def wrapper(self) -> _BY:
            self.__by = func.__name__.replace('_', ' ').lower()
            return self

        return wrapper
    

    # INSTANCE METHODS
    def by(self, by: str) -> _BY:
        self.__by = by
        return self


    # PROPERTIES (BY STRATEGIES)
    @property
    @__sets_by
    def CLASS_NAME(): ...

    @property
    @__sets_by
    def CSS_SELECTOR(): ...

    @property
    @__sets_by
    def ID(): ...

    @property
    @__sets_by
    def LINK_TEXT(): ...

    @property
    @__sets_by
    def NAME(): ...

    @property
    @__sets_by
    def PARTIAL_LINK_TEXT(): ...

    @property
    @__sets_by
    def TAG_NAME(): ...

    @property
    @__sets_by
    def XPATH(): ...


LOCATE = _LOCATE()