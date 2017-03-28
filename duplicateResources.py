from hs_restclient import HydroShare, HydroShareAuthBasic
import bs4
import requests

base_url = 'https://csdms.colorado.edu/wiki/Hydrological_Models'
response = requests.get(base_url)
response.raise_for_status()  # if there is an error in reading the webpage
# this is the html read from the webpage
soup = bs4.BeautifulSoup(response.text, "html.parser")
# selecting the <a> tags, which contain the name
names = soup.select('td > a')
# selecting all of the abstracts (<small> tag)
blurbs = soup.select('td > small')

models = []

for element in names:  # Getting each CSDMS title
    models.append(element.get('title').replace('Model:', '', 1))

auth = HydroShareAuthBasic(username='emorgan117', password='h#nX^d-WR9cC')
hs = HydroShare(auth=auth)

generatorResourceList = hs.getResourceList(types="ModelProgramResource")
uploadedCSDMSgenerator = hs.getResourceList(types="ModelProgramResource", owner="emorgan117")

uploadedCSDMSmodels = []
for mp in uploadedCSDMSgenerator:
    uploadedCSDMSmodels += [mp['resource_title']]

duplicateModelPrograms = {}
for mp in generatorResourceList:
    if mp['resource_title'] in models:
        duplicateModelPrograms[mp['resource_title'].__str__()] = mp['creator']
for element in duplicateModelPrograms:
    print(element + ": \'" + duplicateModelPrograms[element] + "\'")
