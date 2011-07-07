import json
from urllib import urlencode
from urllib2 import quote, urlopen, HTTPError, URLError

class ChEMBLWS(object):
    '''
    '''
    def __init__(self):
        '''
        '''
        self._url = 'https://www.ebi.ac.uk/chemblws/{type}/{chembl_id}.json'

    def _get_instance(self, type, chembl_id):
        '''
        '''
        try:
            response = urlopen(self._url.format(type=type, chembl_id=chembl_id))
            return json.loads(response.read())

        except HTTPError, error:
            if error.code == 404: print 'Nothing found for ChEMBL identifier {chembl_id}.'.format(chembl_id=chembl_id)
            else: print 'HTTP Error code: {code}'.format(code=error.code)

        except URLError, error:
            pass

    def get_compound(self, chembl_id):
        '''
        '''
        return self._get_instance('compounds', chembl_id)

    def get_target(self, chembl_id):
        '''
        '''
        return self._get_instance('targets', chembl_id)

    def get_assay(self, chembl_id):
        '''
        '''
        return self._get_instance('assays', chembl_id)

    def get_targets(self):
        '''
        '''
        pass