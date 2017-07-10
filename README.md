# Research-Scraper

## Simple Introduction

Google Scholar has become a quasi-standard tool for listing publications associated with individual researchers worldwide. However, Google Scholar (and similar tools), does not provide the functionality to capture publications associated with a group of researchers, such as formal or informal research groups (ADAC, IMA, ASAP). As it is often important to research groups to capture their groups’ publications in a coherent listing, e.g., on their website, a tool which can scrape information from individuals’ Google Scholar pages, look for tags such as group names, and then generate purpose-built listings would be of considerable use.
 
## Key requirements:

  + Provide a UI which enables an administrator to select individual research profiles and to add them to a group.
  + Provide functionality to enable the administrator to provide search tags such as research group names
  + Retrieve publication information from Google Scholar or similar
  + Parse PDFs of publications to look for search tags
  + Generate result databases of group publications
  + Provide various output methods for the databases, incl. a structured HTML page which can be included in a website

## Structure Declaration

The project can be basically didived into two parts : 

1. Crawler part : mainly use the famous web crawler framework scrapy, which is easy to install and deploy. This part will focus on fetching data about authors and their papers  from google scholar. The are several key points :
    + make sure we have a quick crawling speed while facing the google's anti-crawler technique. So disguisining methods like setting pseudo user-agent, changing ip agent constantly and regualr sleeping after every request have been used.
    + do regualr update check. i.e, if google scholar update some details in somewhere then do corresponding update for that part. -- TODO

2. Web part : provide the basic interface to the user with a good extensibility as well. I use the complete back-front end separation to implment it.  i.e, the server side does nothing except providing necessary api, and the client side handle all representive layer rendering job only with the json-format data responsed from back end.

   + for a better development effeiciecy, I use the light framework vue, for the front end development and flask for the back end development.
   + to make a the api interface as clear as I can, I use the RESTful concept when providing those API.

## Running Requirement

1. python3
2. scrapy
3. flask




  
 
