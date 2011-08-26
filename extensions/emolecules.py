"""
This extension is used to access and query an eMolecules database.
"""

from sqlalchemy import Table
from sqlalchemy.orm import mapper
from sqlalchemy.sql.expression import and_, func, text
from sqlalchemy.ext.hybrid import hybrid_method

from ..meta import engine, metadata, session
from ..models.model import Model

class Emolecule(Model):
    '''
    Represents a molecule from the eMolecules database.
    
    Attributes
    ----------
    emolecule_id: int
        Primary key.
    smiles: str
        SMILES.
    '''
    def __repr__(self):
        '''
        '''
        return "<eMolecule({self.emolecule_id})>".format(self=self)

    @hybrid_method
    def like(self, smiles):
        '''
        Returns an SQL function expression that uses the PostgreSQL trigram index
        to compare the SMILES strings.
        '''
        warn("Trigram functions at the instance level are not implemented.", UserWarning)

    @like.expression
    def like(self, smiles):
        '''
        Returns an SQL function expression that uses the PostgreSQL trigram index
        to compare the SMILES strings.
        '''
        return self.smiles.op('%%')(smiles)

class EmoleculeAdaptor(object):
    '''
    '''
    def fetch_by_emolecule_id(self, emolecule_id):
        '''
        '''
        return session.query(Emolecule).get(emolecule_id)

    def fetch_all_by_trgm_sim(self, smiles, *expressions, **kwargs):
        '''
        Returns all molecules that are similar to the given SMILES string using
        trigam similarity (similar to LINGO).
        
        By far the quickest way to get similar molecules!

        Parameters
        ----------
        threshold : float, default=0.6
            Similarity threshold that will be used for searching.
        limit : int, default=25
            Maximum number of hits that will be returned.

        Returns
        -------
        resultset : list
            List of tuples (Emolecule, similarity) containing the chemical components
            and the calculated trigram similarity.

        Queried Entities
        ----------------
        Emolecule

        Examples
        --------

        Requires
        --------
        .. important:: `pg_trgm  <http://www.postgresql.org/docs/current/static/pgtrgm.html>`_ PostgreSQL extension.

        Notes
        -----
        Will make use of the KNNGIST operator <-> in 9.1.
        '''
        threshold = kwargs.get('threshold', 0.6)
        limit = kwargs.get('limit', 25)

        # SET THE SIMILARITY THRESHOLD FOR THE INDEX
        session.execute(text("SELECT set_limit(:threshold)").execution_options(autocommit=True).params(threshold=threshold))

        similarity = func.similarity(Emolecule.smiles,smiles).label('similarity')

        query = session.query(Emolecule, similarity)
        query = query.filter(and_(Emolecule.like(smiles), *expressions))
        query = query.order_by(similarity.desc()).limit(limit)

        return query.all()

emolecules_table = Table('compounds', metadata, autoload=True, autoload_with=engine, schema='emolecules')

mapper(Emolecule,emolecules_table)