from ..meta import *
from ..models.chain import Chain
from ..models.interface import Interface

class InterfaceAdaptor(object):
    '''
    '''
    def fetch_by_interface_id(self, interface_id):
        '''
        Parameters
        ----------
        interface_id : int
            Primary key of the `Interface` in CREDO.

        Returns
        -------
        Interface
            CREDO `Interface` object having this interface_id as primary key.

        Examples
        --------
        >>> InterfaceAdaptor().fetch_by_interface_id(1)
        <Interface(1)>
        '''
        return session.query(Interface).get(interface_id)

    def fetch_all_by_biomolecule_id(self, biomolecule_id):
        '''
        Returns a list of `Interface`.

        Parameters
        ----------
        biomolecule_id : int
            `Biomolecule` identifier.

        Returns
        -------
        interfaces : list
            List of `Interface` objects.

         Examples
        --------
        >>> InterfaceAdaptor().fetch_all_by_biomolecule_id(1)
        >>> <Interface()>
        '''
        query = session.query(Interface).filter(Interface.biomolecule_id==biomolecule_id)

        return query.all()
