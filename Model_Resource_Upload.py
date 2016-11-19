from bs4 import BeautifulSoup
import json
from hs_restclient import HydroShare, HydroShareAuthBasic
import bs4
import requests

base_url = 'https://csdms.colorado.edu/wiki/Hydrological_Models'
response = requests.get(base_url)
response.raise_for_status() # if there is an error in reading the webpage
soup = bs4.BeautifulSoup(response.text, "html.parser") #this is the html read from the webpage

names = soup.select('td > a') # selecting the <a> tags, which contain the name and metadata page for each model
blurbs = soup.select('td > small') # selecting all of the abstracts (<small> tag)

models = []     # each element in models has: [0]: model name, [1]: model's CSDMS page, [2]: model's blurb
item = []

for element in names:  # getting the metadata webpage and title for each model
    item = []
    item.append(element.get('title').replace('Model:', '', 1))
    item.append(element.get('href'))
    models.append(item)

for element in blurbs:  # gets the blurb for each model
    models[blurbs.index(element)].append(element.string.replace('E-book: ', ''))
   #  print(models[blurbs.index(element)])

#  next, the crawler goes into each model's CSDMS webpage and gets the fields to input to Hydroshare
for model in models:
    page_url = 'https://csdms.colorado.edu' + model[1] # so we can get to each model's page
    response = requests.get(page_url)
    response.raise_for_status()  # if there is an error in reading the webpage
    page = bs4.BeautifulSoup(response.text, "html.parser")  # this is the html read from the webpage
    fields = page.select('tr > td[class=model_col1]')
    answers = page.select('tr > td[class=model_col2]')

    # hydro_fields is a list of all the field names that both Hydroshare and CSDMS have
    hydro_fields = ['Keywords:', "First name", "Last name", "Institute / Organization",
                    "Email address", "Postal address 1", 'Town / City', 'Postal code', 'State', 'Country', "Phone",
                    "Describe post-processing software", "Start year development",
                    "Programming language", "Source web address", "Supported platforms", "Extended model description"]
    machinegendata = {}  # the scraped fields

    for i in range(0, fields.__len__()): # go through each of the fields for each model
        if hydro_fields.__contains__(fields[i].getText().strip('\n').lstrip(' ')):
            # print(fields[i].getText().strip('\n').lstrip(' '))
            machinegendata[fields[i].getText().strip('\n').lstrip(' ')] = answers[i].getText().strip('\n')
            # print(machinegendata[fields[i].getText().strip('\n').lstrip(' ')])
    machinegendata['Title'] = model[0]  # getting the model name and putting it in

    # This is the second part of the program--taking the data contained in machinegendata and uploading it to Hydroshare
    auth = HydroShareAuthBasic(username='XXXXX', password='XXXXXXXX')
    hs = HydroShare(auth=auth)
    name = machinegendata['First name'] + ' ' + machinegendata['Last name']
    address = machinegendata['Postal address 1'] + ' ' + machinegendata['Town / City'] + ' ' + machinegendata['State'] \
              + ' ' + machinegendata['Country'] + ' ' + machinegendata['Postal code']

    # TODO: what are the json fields that I can write metadata to?
    # TODO: Get the model manuals off of CSDMS and put them on Hydroshare
    meta = [{"MpMetadata": {
        "modelProgramLanguage": machinegendata["Programming language"]
    }}]

    resource_id = hs.createResource("ModelProgramResource",
                                    title=machinegendata['Title'],
                                    abstract=machinegendata['Extended model description'],
                                    metadata=json.dumps(meta))
                                    #keywords=[machinegendata['Keywords:']])

    break #test on Anuga only