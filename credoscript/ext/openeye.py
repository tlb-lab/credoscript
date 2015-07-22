"""
This extension adds support for the OpenEye PostgreSQL cartridge.
"""
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql.expression import and_, func, text

from credoscript import Base, schema, Session
from credoscript.adaptors import ChemCompAdaptor
from credoscript.mixins.base import paginate

class ChemCompOEFP(Base):
    '''
    '''
    __tablename__ = '%s.chem_comp_oefps' % schema['pdbchem']

    ChemComp = relationship("ChemComp",
                            primaryjoin="ChemCompOEFP.het_id==ChemComp.het_id",
                            foreign_keys="[ChemComp.het_id]",
                            uselist=False, innerjoin=True,
                            backref=backref('OEFP', uselist=False, innerjoin=True))

    def __repr__(self):
        '''
        '''
        return '<ChemCompOEFP({self.het_id})>'.format(self=self)

class ChemCompAdaptor(ChemCompAdaptor):
    """
    """
    @paginate
    def fetch_all_by_sim_oe(self, smiles, *expr, **kwargs):
        """
        Returns all Chemical Components that match the given SMILES string with at
        least the given similarity threshold using chemical fingerprints.

        Parameters
        ----------
        smi : str
            The query rdmol in SMILES format.
        threshold : float, default=0.5
            The similarity threshold that will be used for searching.
        fp : {'circular','atompair','torsion'}
            RDKit fingerprint type to be used for similarity searching.
        *expr : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried Entities
        ----------------
        ChemComp, ChemCompOEFP

        Returns
        -------
        hits : list
            List of tuples in the form (ChemComp, similarity)

        Examples
        --------

        Requires
        --------
        .. important:: OpenEye cartridge.
        """
        session = Session()

        threshold = kwargs.get('threshold')
        metric = kwargs.get('metric','tanimoto')
        fp = kwargs.get('fp', 'circular')
        limit = kwargs.get('limit', 100)

        # set the similarity threshold for the selected metric
        if threshold:
            statement = text("SELECT openeye.set_oefp_similarity_limit(:threshold, :metric)")
            session.execute(statement.params(threshold=threshold,metric=metric))

        if fp == 'circular':
            query = func.openeye.make_circular_fp(smiles)
            target = ChemCompOEFP.circular_fp

        elif fp == 'maccs166':
            query = func.openeye.make_maccs166_fp(smiles)
            target = ChemCompOEFP.maccs166_fp

        elif fp == 'path':
            query = func.openeye.make_path_fp(smiles)
            target = ChemCompOEFP.path_fp

        elif fp == 'tree':
            query = func.openeye.make_tree_fp(smiles)
            target = ChemCompOEFP.tree_fp

        else:
            raise ValueError("cannot create fingerprint: type {0} does not exist."
                             .format(fp))

        # compile similarity metric and the correspoding GIST index / KNN-GIST
        if metric == 'tanimoto':
            similarity = func.openeye.tanimoto(query, target)
            index = func.openeye.tanimoto_is_above_limit(target, query)
            orderby = target.op('OPERATOR(openeye.<%%>)')(query) # escape %

        elif metric == 'dice':
            similarity = func.openeye.dice(query, target)
            index = func.openeye.dice_is_above_limit(target, query)
            orderby = target.op('OPERATOR(openeye.<#>)')(query)

        elif metric == 'manhattan':
            similarity = func.openeye.manhattan(query, target)
            index = func.openeye.manhattan_is_above_limit(target, query)
            orderby = target.op('OPERATOR(openeye.<~>)')(query)

        elif metric == 'cosine':
            similarity = func.openeye.cosine(query, target)
            index = func.openeye.cosine_is_above_limit(target, query)
            orderby = target.op('OPERATOR(openeye.<@>)')(query)

        elif metric == 'euclidean':
            similarity = func.openeye.euclidean(query, target)
            index = func.openeye.euclidean_is_above_limit(target, query)
            orderby = target.op('OPERATOR(openeye.<->)')(query)

        else:
            raise ValueError("{} is not a valid similarity metric.".format(metric))

        query = ChemComp.query.add_column(similarity)
        query = query.join('OEFP').filter(and_(index, *expr))
        query = query.order_by(orderby)

        return query

from credoscript.models.chemcomp import ChemComp