from sqlalchemy.sql.expression import and_

from ..meta import session

class XRefAdaptor(object):
    '''
    '''
    def __init__(self):
        '''
        '''
        self.query = session.query(XRef)

    def fetch_by_xref_id(self, xref_id):
        '''
        '''
        return self.query.get(xref_id)

    def fetch_all_by_entity(self, entity_type, entity_id, *expressions):
        '''
        Returns all the cross references associated with this Entity.

        Parameters
        ----------
        entity_type : str
            Type of the entity, e.g. 'Structure'.
        entity_id : int
            Primary key of the entity in CREDO.
        *expressions : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried Entities
        ----------------
        XRef

        Returns
        -------
        xrefs : list
            All the cross references associated with the given Entity.
        '''
        return self.query.filter(and_(XRef.entity_type==entity_type,
                                      XRef.entity_id==entity_id,
                                      *expressions)).all()

from ..models.xref import XRef