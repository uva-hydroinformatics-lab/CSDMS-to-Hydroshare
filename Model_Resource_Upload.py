from bs4 import BeautifulSoup
import json
from hs_restclient import HydroShare, HydroShareAuthBasic
import bs4
import requests

base_url = 'https://csdms.colorado.edu/wiki/Hydrological_Models'
response = requests.get(base_url)
response.raise_for_status()  # if there is an error in reading the webpage
# this is the html read from the webpage
soup = bs4.BeautifulSoup(response.text, "html.parser")
# selecting the <a> tags, which contain the name and metadata page for
# each model
names = soup.select('td > a')
# selecting all of the abstracts (<small> tag)
blurbs = soup.select('td > small')

models = []     # each element in models has: [0]: model name, [1]: model's CSDMS page, [2]: model's blurb
item = []

for element in names:  # getting the metadata webpage and title for each model
    item = []
    item.append(element.get('title').replace('Model:', '', 1))
    item.append(element.get('href'))
    models.append(item)

# gets the blurb for each model
# replace E-book: with '' because on some model blurbs, it puts E-book: for some reason
for element in blurbs:
    models[blurbs.index(element)].append(element.string.replace('E-book: ', ''))

# next, the crawler goes into each model's CSDMS webpage and gets the
# fields to input to Hydroshare
for model in models:
    softwareRepo = False #if the website is a repo site (github, sourceforge) or not
    if(model[0] == 'GEOtop'):
        # so we can get to each model's page
        page_url = 'https://csdms.colorado.edu' + model[1] 
        response = requests.get(page_url)
        response.raise_for_status()  # if there is an error in reading the webpage
        
        # this is the html read from the webpage
        # fields is a list of the scraped definitions from the HTML for each model (items)
        # answers is a list of the scraped inputs from the HTML for each model (descriptions of items)
        page = bs4.BeautifulSoup(response.text, "html.parser")
        fields = page.select('tr > td[class=model_col1]')
        answers = page.select('tr > td[class=model_col2]')
        
        # hydro_fields is a list of all the field names that both Hydroshare and CSDMS have
        hydro_fields = ['Keywords:', "First name", "Last name", "Institute / Organization",
                        "Email address", "Postal address 1", 'Town / City', 'Postal code', 'State', 'Country', "Phone",
                        "Describe post-processing software", "Start year development",
                        "Programming language", "Source web address", "Source csdms web address", "Supported platforms", 
                        "Extended model description"]
        
        machinegendata = {}  # a dictionary of the scraped fields & their responses
        # go through each of the fields for each model
        for i in range(0, fields.__len__()):
            # matching up the fields we want (hydro_fields) to those scraped from CSDMS (fields)
            if hydro_fields.__contains__(fields[i].getText().strip('\n').lstrip(' ')):
                # if the CSDMS addre    ss i github or sourceforge repo, put it in the software repository field
                # else, put it in the website field
                if(fields[i].getText().strip('\n').lstrip(' ') == "Source web address" and "sourceforge" in answers[i].getText() or
                   fields[i].getText().strip('\n').lstrip(' ') == "Source web address" and "github" in answers[i].getText()):
                    machinegendata["Software Repository"] = answers[i].getText().strip('\n')
                    softwareRepo = True
                # "Source web address" and "Source csdms web address" may both refer to the main webpage
                # If the csdms web address is given in addition to the web address, it will overwrite the regular web address field
                elif(fields[i].getText().strip('\n').lstrip(' ') == "Source csdms web address" and "sourceforge" in answers[i].getText() or
                   fields[i].getText().strip('\n').lstrip(' ') == "Source csdms web address" and "github" in answers[i].getText()):
                    machinegendata["Software Repository"] = answers[i].getText().strip('\n')
                    softwareRepo = True
                else:
                    machinegendata[fields[i].getText().strip('\n').lstrip(' ')] = answers[i].getText().strip('\n')
        # getting the model name and putting it in
        machinegendata['Title'] = model[0]

        # This is the second part of the program--taking the data contained in
        # machinegendata and uploading it to Hydroshare
        auth = HydroShareAuthBasic(username='XXXXXXXXXXX', password='XXXXXXXXXX')
        hs = HydroShare(auth=auth)
        name = machinegendata['First name'] + ' ' + machinegendata['Last name']
        address = machinegendata['Postal address 1'] + ' ' + \
          machinegendata['Town / City'] + ' ' + machinegendata['State'] \
          + ' ' + machinegendata['Country'] + ' ' + machinegendata['Postal code']

        # if the CSDMS webpage is a github or sourceforge repo, put it in the software repo field
        # else, just put it in the Website field
        if(softwareRepo):
            meta = [{"mpmetadata": {
                "modelProgramLanguage": machinegendata["Programming language"],
                "modelOperatingSystem": machinegendata["Supported platforms"],
                "modelReleaseDate": machinegendata["Start year development"],
                "modelCodeRepository": machinegendata["Software Repository"],
                "modelSoftware": machinegendata["Describe post-processing software"]

            }}]
        else:
         meta = [{"mpmetadata": {
                "modelProgramLanguage": machinegendata["Programming language"],
                "modelOperatingSystem": machinegendata["Supported platforms"],
                "modelReleaseDate": machinegendata["Start year development"],
                "modelWebsite": machinegendata["Source web address"] ,
                "modelSoftware": machinegendata["Describe post-processing software"]

            }}] 

        resource_id = hs.createResource("ModelProgramResource",
                                    title=machinegendata['Title'],
                                    abstract=machinegendata['Extended model description'],
                                    keywords=[machinegendata['Keywords:']],
                                    metadata=json.dumps(meta))

        #Does the current createResource allow for me to set a creator? The hsapi/createResource page
        #was updated recently and it now has space for a creator to be added, but I can't find anywhere in the
        #API that supports adding a creator. I've got the fields we wanted to add in, with the exception of documentation
        #which I need to work on after I get the authors thing worked out.
        break  # test on Anuga only
