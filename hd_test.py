from hs_restclient import HydroShare, HydroShareAuthBasic
import bs4

hs = HydroShare()
science_md = hs.getScienceMetadata('ba94cc37e8f1409d8bd515bb49bd955e')
resource_md = hs.getSystemMetadata('ba94cc37e8f1409d8bd515bb49bd955e')
soup = bs4.BeautifulSoup(science_md, "html.parser") #this is the html read from the webpage
soup.prettify()
print(soup)