## Group Design Practical - Group 3

### Introduction:
A project developed for the 2nd Year Group Design Practical of the Computer Science Course 
at the University of Oxford. It aims to be web application that can be used as a minimalist 
survival guide for confused tourist, built using data gathered from Twitter users. It is simple 
enough to be used by any tourist and offers support for any trip location.

At the moment, the four main uses are:
(1) getting the Language Distribution of Tweets in any circular area;
(2) building a Word Cloud of the most frequent words in the area viewed by the User;
(3) obtaining the Official Twitter Timeline of any Place of Interest;
(4) obtaining the Twitter Users' Opinion about any Place of Interest.

Of Note: (1) and (2) depend on the sample space of Tweets gathered and stored in a MongoDB database.

### Setting Up:
1. Using git clone the project in the folder of your choosing (alternatively download and copy the files).
2. Install Python 2.7.9. Make sure Pip is installed (otherwise install it).
3. Install VirtualEnv, by typing in the terminal of your choice:
    pip install virtualenv
4. Go to the project folder and create a directory called env.
5. In terminal, write:
    virtualenv env
   to create the virtual environment.
6. Setup the Environment Variables, either in the System or by changing the activation script.
   The following are required:
        TWITTER_ACCESS_TOKEN
        TWITTER_ACCESS_TOKEN_SECRET
        TWITTER_CONSUMER_KEY
        TWITTER_CONSUMER_SECRET
        ALCHEMYAPI_KEY
        MONGOLAB_URI
   First four will be provided by Twitter, the fifth can be obtained from the AlchemyAPI, while the sixth
   is the URI to the MongoDB database.
   If the activation script is changed to set these variables make sure to unset them in the deactivation script.
   
   For Windows users, the activation/deactivation scripts are activate.bat and deactivate.bat in env\Scripts\.
   Just open any text editor of choice, and add: 
    in activate.bat:
        set "[VAR_NAME]=[VAR_VALUE]"
    in deactivate.bat:
        set [VAR_NAME]=
    [VAR_NAME] is to be replaced with actual name of the Environment Variable, while [VAR_VALUE] with the actual value you
    want to use for them.
    It is possible to set the Variables for the other Operating Systems (probably easier).
7. Activate Virtual Environment.
    on Windows: run from terminal: env\Scripts\activate
8. Install prerequisites:
    pip install -r requirements.txt
9. Once usage is finished: run deactivate.

Notes: it is possible to run without virtualenv, although it means that all the Environment Variables and the prerequisites 
have to be installed on the System.

### Gathering Data:
    When the environment is set up, in the folder of the project open a terminal and run:
        python crawler.py
    To change the Area from which data is to be gathered:
        open crawler.py
        close to the very end, there is a line for assigning twitter_stream
        in the filter, change the name of the country to the one you prefer
    The data representing the area-boxes of each country is in the countries file in the project. 
    If any other area are desired to be added:
        write a new line containing name of country, longitude for SW point, latitude for SW point, longitude for NE point, latitude for NE point.
    
### Running the API:
    When the environment is set up, in the folder of the project open a terminal and run:
        python api.py
    The API can also be run on a server to allow non-local connections.
    
### Importing Sample Data:
    In the folder database inside of the project, two JSON files have been provided, containing the processed data of 20k tweets.
    They can be imported in the MongoDB database of your choosing by using mongoimport.
    More info about the function at the link:
        http://docs.mongodb.org/v2.2/reference/mongoimport/
        
### Other notes:
Information about setting up the MongoDB database can be found on http://mongodb.org/

    
### PROJECT Short Report:
https://docs.google.com/document/d/1XcYPHL3daBo8hvT-WK46V7qpLmzpyzEWWaQRk6J94kY/edit?usp=sharing

### PROJECT Long Report:
https://docs.google.com/document/d/1-L9ZlJrEFOkF_HBKKI0fdbeh5nAImPiE6juvJwK7Bi8/edit

### Project Specification (still a draft):
https://docs.google.com/document/d/1Oz8P191NhYcW2F_nyWKXUU-yRKX1a-aY3NyEmdrjpIo/edit?usp=sharing

### Credits:
Group 3:
    Alexander Bridgland
    Toby Cathcart Burn
    Dan-Andrei Gheorghe
    Paul-Stefan Herman
    Mariya Lazarova
Under the supervision of:
    Dr. Jason Nurse
    Dr. Ioannis Agrafiotis
    Dr. Arnau Erola
    
