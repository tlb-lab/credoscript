from urllib import urlencode
from urllib2 import quote, urlopen, HTTPError

class ChemIdResolver(object):
    '''
    The service returns the requested new structure representation with a corresponding
    MIME-Type specification (in most cases MIME-Type: "text/plain"). If a requested
    URL is not resolvable for the service an HTML 404 status message is returned.
    In the (unlikely) case of an error, an HTML 500 status message is generated.
    '''
    def __init__(self):
        '''
        '''
        self._url = 'http://cactus.nci.nih.gov/chemical/structure/{id}/{representation}'

    def get_smiles(self, id, resolver=None):
        '''
        Returns the Unique SMILES of the structure as calculated by the
        chemoinformatics toolkit CACTVS.

        Available resolvers:
            smiles
            stdinchikey
            stdinchi
            ncicadd_identifier
            hashisy
            cas_number
            name
        '''
        url = self._url.format(id=quote(id), representation='smiles')

        # ADD A SPECIFIC RESOLVER IF GIVEN
        if resolver: url = '?'.join((url, 'resolver={rslvr}'.format(rslvr=resolver)))

        try:
            response = urlopen(url)
            return response.read()

        except HTTPError, error:
            if error.code == 404: print 'Nothing found.'
            else: print 'HTTP Error code: {code}'.format(code=error.code)

    def get_synonyms(self, id, resolver=None):
        '''
        Returns a list of chemical names for the structure. The names currently
        available via this method comprises trivial names, systematic names,
        registry numbers and original structure provider IDs.
        Note that not all entries in our database have a name associated with them.
        '''
        url = self._url.format(id=quote(id), representation='names')

        # ADD A SPECIFIC RESOLVER IF GIVEN
        if resolver: url = '?'.join((url, 'resolver={rslvr}'.format(rslvr=resolver)))

        try:
            response = urlopen()
            return response.read().strip().split('\n')

        except HTTPError, error:
            if error.code == 404: print 'Nothing found.'
            else: print 'HTTP Error code: {code}'.format(code=error.code)

    def get_structure(self, id, format='sdf', get3d=False):
        '''
        '''
        url = self._url.format(id=id,representation='file')
        url += '?'
        url += urlencode({'format':format,'get3d':get3d})

        try:
            response = urlopen(url)
            return response.read().strip()

        except HTTPError, error:
            if error.code == 404: print 'Nothing found.'
            else: print 'HTTP Error code: {code}'.format(code=error.code)