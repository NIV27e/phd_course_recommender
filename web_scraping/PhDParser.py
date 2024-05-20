import lxml
import os
import requests
import json
from bs4 import BeautifulSoup
import discipline_dict
import warnings
from datetime import datetime
from collections import defaultdict

class Parser():
    def __init__(self):
        self.disciplines = discipline_dict.disciplines

    def parseURL(self, url) -> BeautifulSoup:
        """ Returns 'soup' object from a html page using requests and BeautifulSoup. 
            url (str) : valid findaPhD url to parse
            RETURNS BeautifulSoup : BeautifulSoup object used to parse data
        """
        return BeautifulSoup(requests.get(url).text, 'lxml')
    
    def readJson(self, file_path) -> (json):
        """ Reads .json file and returns it as a variable. """
        with open(file_path, 'r') as file:
            return(json.load(file))

    def saveAsJson(self, contents:(list[dict]), file_path:str="json"):
        """ Saves list of dictionaries as .json file. 
            contents (list[dict]) : contents to save in .json file
            file_path (str) : path to save, including filename. can be relative. defaults to json + the lowest integer unused by an existing 'json' file
        """
        if file_path == "json": 
            i = 1
            while True:
                try: open(f"str{i}.json")
                except FileNotFoundError: break
                else: i+=1
            file_path = f"str{i}.json"
            
        with open(file_path, 'w') as json_file:
            json.dump(contents, json_file, indent=2)

class DisciplineParser(Parser):
    """ Parses the 'disciplines' page on findaphd.com to return all discipline url codes. """

    def __init__(self):
        super().__init__()  # initialise parent class
        self.url = "https://www.findaphd.com/phds/discipline/"
        self.soup = self.parseURL(self.url)
    
    def scrapeDisciplines(self) -> dict:
        """ Scrapes discipline page and returns dictionary of disciplines. """
        discipline_containers = self.soup.find_all(class_="card-title text-dark h4 d-block")

        for discipline_container in discipline_containers:
            if discipline_container is None: continue
            title = discipline_container.get_text(strip=True).lower()
            link_suffix = discipline_container.get('href')
            if title not in self.disciplines:
                self.disciplines[title] = link_suffix
        return self.disciplines

class PhDParser(Parser):
    """ Class to handle all (previous and current) searches for PhDs. Each instance handles a single new search. 
        all_projects (defaultdict[dict]) : dict of search terms, storing a dict of project names, each with a dict of saved projects for that search term. 
    """
    # Load class variables
    discipline_dict = discipline_dict.disciplines
    all_projects = defaultdict(dict)
    tmp_json = {}
    if os.path.exists('all.json'):
        with open('all.json', 'r') as file:
            tmp_json = json.load(file)
    all_projects.update(tmp_json)

    def __init__(self, discipline:str="", recent_only:bool=True, keywords:str=""):
        """ Saves results of search to self.current_projects variable.
            discipline (str) : discipline of study to search within. default is "psychology"
            recent_only (bool) : show only recent PhD opportunities. default is True
            keywords (str) : *comma separated* list of search terms. defaults to no terms
        """
        super().__init__()  # initialise parent class

        # Checks for valid inputs
        discipline = discipline.lower()
        if discipline not in self.discipline_dict: raise Exception('invalid discipline chosen! See `disciplines.py` for current list of valid disciplines...')

        # Generate url and use it to obtain and parse HTML soup
        self.url, self.search_string = self.genURL(discipline=discipline, recent_only=recent_only, keywords=keywords)  # generate search url and search string
        self.soup = self.parseURL(self.url)
        self.current_projects = self.parsePhdSoup(self.soup)  # parse soup data

        if self.current_projects == {}:
            warnings.warn('There are currently no PhDs listed using your search terms:/ Feel free to try again with different terms.')
        
        # Add current_projects to all_projects, stored under the search string
        self.all_projects[self.search_string].update(self.current_projects)

    def saveCurrentAsJson(self, file_path:str="recent.json"):
        """ Saves recent new projects as a .json file with given output path. 
            file_path (str) : path to save projects to. default is "recent.json" in current directory.
        """
        if self.current_projects == {}: raise Exception('No recent projects to save!')
        self.saveAsJson(self.current_projects, file_path=file_path)

    def saveAllAsJson(self, file_path:str="all.json"):
        """ Saves all projects as a .json file with given output path. 
            file_path (str) : path to save projects to. default is "recent.json" in current directory.
        """
        self.saveAsJson(self.all_projects, file_path=file_path)

    # ~~~~~ INTERNAL FUNCTIONS - do not need to be called by user. ~~~~~
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def genURL(self, discipline:str="", recent_only:bool=True, keywords:str="") -> str:
        """ Generates a valid findaPhD url using search keywords. 
            discipline (str) : discipline of study to search within. default is "psychology"
            recent_only (bool) : show only recent PhD opportunities. default is True
            keywords (str) : *comma separated* list of search terms. defaults to no terms
            RETURNS str : valid findaPhD url
        """
        if discipline not in self.disciplines: raise KeyError("not a valid subject!")
        if discipline == "" and keywords == "": raise ValueError("you must include either a discipline or a keyword to search for PhDs.")

        url_list = [f"https://www.findaphd.com{self.disciplines[discipline]}"]
        if recent_only: url_list.append("Show=M")

        keywords_list = sorted([item.strip() for item in keywords.split(',')])
        keywords_str = ("+").join(keywords_list)
        url_list.append(f"keywords={keywords_str}")

        url = '&'.join(url_list)  # combine url, joined with '&'s
        search_string = f"{discipline}&{keywords_str}"  # save hashstring of search term
        print(f"search = {search_string}")
        return url, search_string

    def parsePhdSoup(self, soup:BeautifulSoup) -> dict[dict]:
        """ Returns list of new PhD projecst using BeautifulSoup data. 
            soup (BeautifulSoup) : BeautifulSoup data for a findaPhD search page
            RETURNS dict[dict] of project traits, stored under project names
        """
        current_projects = {}
        phd_containers = soup.find_all(class_="w-100 card shadow-sm p-4")

        # Extra data from each project title individually.
        for container in phd_containers:
            # Get information from title
            title_container = container.find(class_="h4 text-dark mx-0 mb-3")
            link = f"https://www.findaphd.com{title_container['href']}"  # generate link to page
            title = title_container.text  # generate title

            # Process hashstring
            if title in self.all_projects[self.search_string]: continue  # don't reprocess if already in set

            # Time accessed
            access_time = datetime.now().isoformat()  # convert datetime to string

            # Get information about PhD country from the 'flag' section
            country = container.find(class_="phd-result__dept-inst--country-icon")
            if country is not None:  country = country.get("title")

            # Get university name
            university = container.find(class_="phd-result__dept-inst--title")
            if university is not None: university = university.get_text(strip=True)
            
            # Get date of last update
            date_updated = container.find(class_="apply py-2 small")
            if date_updated is not None: date_updated = date_updated.get_text(strip=True)[8:]

            # Get deadline date
            deadline = container.find(class_="fa-calendar")
            if deadline is not None: deadline = deadline.parent.get_text(strip=True)

            # Get funding information
            funding = container.find(class_="fa-wallet")
            if funding is not None: funding = funding.parent.get_text(strip=True)

            # Append to list and return
            current_projects[title] = {
                "title": title,
                "date_updated": date_updated,
                "deadline": deadline,
                "access_time": access_time,
                "funding": funding,
                "link": link,
                "country": country,
                "university": university
            }
        return current_projects