from sqlalchemy import Integer
from sqlalchemy.sql.expression import and_, cast, func, text

from credoscript import citations
from credoscript.mixins.base import paginate

class StructureAdaptor(object):
    """
    Class to fetch Structure objects from CREDO with the help of various
    selection criterias.
    """
    def __init__(self, paginate=False, per_page=100):
        self.query = Structure.query
        self.paginate = paginate
        self.per_page = per_page

    def fetch_by_structure_id(self, structure_id):
        """
        Returns the Structure with the given CREDO structure_id.

        Parameters
        ----------
        structure_id : int
            Primary key of the Structure in CREDO.

        Returns
        -------
        Structure
            CREDO Structure object having this structure_id as primary key.

        Examples
        --------
        >>> StructureAdaptor().fetch_by_structure_id(1000)
        <Structure('1B8Q')>
        """
        return self.query.get(structure_id)

    def fetch_by_pdb(self, pdb):
        """
        Returns the Structure matching the given PDB code.

        Parameters
        ----------
        pdb : string
            PDB code (case insensitive) of the Structure in CREDO.

        Returns
        -------
        Structure
            CREDO Structure object having this structure_id as primary key.

        Examples
        --------
        >>> StructureAdaptor().fetch_by_pdb('1OPJ')
        <Structure('1OPJ')>
        """
        return self.query.filter(Structure.pdb==pdb.upper()).first()

    @paginate
    def fetch_all_by_het_id(self, het_id, *expr, **kwargs):
        """
        Returns all the Structures that contain this chemical component as a Ligand.

        Parameters
        ----------
        het_id : str
            Three-letter code of the chemical component that will be used to query
            for structures.
        *expr : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried Entities
        ----------------
        Structure, Biomolecule, Ligand

        Returns
        -------
        structures : list
            All the Structures that contain this chemical component as a Ligand.

        Examples
        --------

        """
        query = self.query.join('Biomolecules','Ligands')
        query = query.filter(and_(Ligand.ligand_name==het_id.upper(), *expr))

        return query.distinct()

    @paginate
    def fetch_all_by_uniprot(self, uniprot, *expr, **kwargs):
        """
        Returns all structures that contain polypeptides having the specified
        UniProt accession.

        Parameters
        ----------
        uniprot : str
            UniProt accession.
        *expr : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried Entities
        ----------------
        Structure, Chain, XRef

        Returns
        -------
        structures : list
            All structures that contain polypeptides having the specified
            UniProt accession.

        Examples
        --------
        >>> StructureAdaptor().fetch_all_by_uniprot('P03372')
        [<Ligand(B 600 OHT)>, <Ligand(A 600 OHT)>,...]
        """
        query = self.query.join('Biomolecules','Chains','XRefs')

        query = query.filter(and_(XRef.source=='UniProt',
                                  XRef.xref==uniprot,
                                  *expr))

        return query.distinct()

    @paginate
    def fetch_all_by_tsquery(self, tsquery, *expr, **kwargs):
        """
        Returns all structures whose abstract matches the keywords given in the
        keyword string.

        Parameters
        ----------
        tsquery : str
            A string containing the lexme that will be used for searching. The
            string will be automatically casted into a tsquery through the to_tsquery()
            function.
        weights : list, default=[0.1, 0.2, 0.4, 1.0]
            The weights specify how heavily to weigh each category of word, in the
            order [D-weight, C-weight, B-weight, A-weight].
        normalization : int, default=32
            Option that specifies whether and how a document's length should impact
            its rank. The integer option controls several behaviors, so it is a
            bit mask: you can specify one or more behaviors using | (for example, 2|4).
            -  0 ignores the document length
            -  1 divides the rank by 1 + the logarithm of the document length
            -  2 divides the rank by the document length
            -  4 divides the rank by the mean harmonic distance between extents
                 (this is implemented only by ts_rank_cd)
            -  8 divides the rank by the number of unique words in document
            - 16 divides the rank by 1 + the logarithm of the number of unique
                 words in document
            - 32 divides the rank by itself + 1
        min_words : int, default=10
        max_words : int, default=25

        Returns
        -------
        resultset : list
            List containing tuples in the form (Structure, snippet, rank).
            The snippet is the part of the abstract that matches the query.
            Ordered by rank.

        Notes
        -----
        - http://www.postgresql.org/docs/current/interactive/datatype-textsearch.html

        Examples
        --------
        >>> StructureAdaptor().fetch_all_by_tsquery('imatinib')
        [(<Structure(3FW1)>,  u'[Imatinib] represents the first in a class', 0.54545500000000002),
        (<Structure(2GQG)>, u'[imatinib], an inhibitor of BCR-ABL. Although', 0.375),
        (<Structure(3CS9)>,  u'[imatinib] against [imatinib]-resistant Bcr-Abl. Consistent', 0.33333299999999999),
        (<Structure(2HYY)>, u'[imatinib] as first-line therapy', 0.230769),
        (<Structure(3G0F)>, u'[imatinib] mesylate and sunitinib malate', 0.230769),
        (<Structure(3G0E)>, u'[imatinib] mesylate and sunitinib malate', 0.230769),
        (<Structure(1T46)>, u'[Imatinib] or Gleevec) demonstrates that', 0.090909100000000007)]
        """
        weights = kwargs.get('weights',[0.1, 0.2, 0.4, 1.0])
        normalization = kwargs.get('normalization', 32)
        min_words, max_words = kwargs.get('min_words', 10), kwargs.get('max_words', 25)

        if kwargs.get('plain'): tsquery = func.plainto_tsquery('english', tsquery)
        else: tsquery = func.to_tsquery('english', tsquery)

        headline_conf = 'StartSel=[, StopSel=], MaxWords={0}, MinWords={1}'.format(max_words, min_words)

        # function to create a preview snippet of the matched area
        snippet = func.ts_headline('english', citations.c.abstract,
                                   tsquery, headline_conf).label('snippet')

        # calculated rank of the hit
        rank = func.ts_rank_cd(weights, func.to_tsvector('english', citations.c.abstract),
                               tsquery, normalization).label('rank')

        # GIST index that is used for searching
        index = func.to_tsvector('english', citations.c.abstract).op('@@')(tsquery)

        query = self.query.filter(and_(*expr))
        query = query.add_columns(snippet, rank)

        query = query.join(XRef, and_(XRef.entity_type=='Structure',
                                      XRef.entity_id==Structure.structure_id))

        query = query.join(citations,
                           and_(citations.c.pubmed_id==cast(XRef.xref, Integer),
                                XRef.source=='PubMed'))

        query = query.filter(index).order_by("rank DESC")

        return query

from ..models.xref import XRef
from ..models.ligand import Ligand
from ..models.biomolecule import Biomolecule
from ..models.structure import Structure