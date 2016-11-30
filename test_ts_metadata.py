import json
from hs_restclient import HydroShare, HydroShareAuthBasic


hs_hostname = "www.hydroshare.org"
auth = HydroShareAuthBasic(username='jsadler', password='hydro')
hs = HydroShare(hostname=hs_hostname, auth=auth)

rtype = 'RefTimeSeriesResource'
title = 'My Test RefTimeSeriesResource'
metadata = []

soap_url = 'http://worldwater.byu.edu/interactive/gill_lab/services/index.php/cuahsi_1_1.asmx?WSDL'
soap_type = "soap"
metadata.append({"referenceurl":
                     {"value": soap_url,
                      "type": soap_type}})
metadata.append({"site": {"code": "network:LC-LA6D5cm"}})
metadata.append({"variable": {"code": "network:GillBYU-SoilTemp"}})



metadata.append({'relation': {'type': 'isPartOf',
                              'value': 'http://hydroshare.org/resource/001'}})

res_id = hs.createResource(rtype,
                           title,
                           resource_file=None,
                           keywords=["kw1", "kw2"],
                           abstract="myabstract",
                           metadata=json.dumps(metadata))
print res_id
hs.setAccessRules(res_id, public=True)