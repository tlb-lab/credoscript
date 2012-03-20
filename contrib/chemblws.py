import json
from urllib import urlencode
from urllib2 import quote, urlopen, HTTPError, URLError

class ChEMBLWS(object):
    '''
    '''
    def __init__(self):
        '''
        '''
        self._url = "https://www.ebi.ac.uk/chemblws/{entity}/{target}/{query}.json"

    def _get_instance(self, entity, target, query):
        """
        """
        url = self._url.format(entity=entity, target=target, query=query)
        
        try:
            response = urlopen(url)   

        except HTTPError, error:
            raise error 
        
        else:
            return json.loads(response.read())

    def compound_bioactivities(self, chembl_id):
        """
        Get individual compound bioactivities
        """
        return self._get_instance('compounds', chembl_id, 'bioactivities')