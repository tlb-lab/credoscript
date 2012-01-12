from sqlalchemy.sql.expression import func, text, and_

from credoscript import session
from credoscript.support import requires

class ChemCompAdaptor(object):
    '''
    Adaptor class to fetch chemical components from CREDO.
    '''
    def __init__(self):
        '''
        '''
        self.query = session.query(ChemComp)

    def fetch_by_chem_comp_id(self, chem_comp_id):
        '''
        '''
        return self.query.get(chem_comp_id)

    def fetch_by_het_id(self, het_id):
        '''
        Returns the ChemComp having the specified HET-ID.
        
        Parameters
        ----------
        het_id : str
            Three-letter code of the chemical component.
        
        Returns
        -------
        chemcomp : ChemComp
            ChemComp having the specified HET-ID
        
        Examples
        --------
        >>>> ChemCompAdaptor().fetch_by_het_id('NIL')
        <ChemComp(NIL)>
        '''
        return self.query.filter(ChemComp.het_id==het_id.upper()).first()

    def fetch_by_residue_id(self, residue_id):
        '''
        '''
        query = self.query.join((Residue, Residue.res_name==ChemComp.het_id))
        query = query.filter(Residue.residue_id==residue_id)
        
        return query.first()

    def fetch_all_by_fragment_id(self, fragment_id, *expressions):
        '''
        Returns all Chemical Components in the PDB that lead to the fragment with
        the given fragment_id during the RECAP fragmention process.

        Parameters
        ----------
        fragment_id : int
            Primary key of the fragment for which all chemical components should
            be returned.
        *expressions : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Returns
        -------
        chemcomps : list
            List of chemical components.

        Examples
        --------

        '''
        query = self.query.join('ChemCompFragments')
        query = query.filter(and_(ChemCompFragment.fragment_id==fragment_id, *expressions))

        return query.all()

    def fetch_all_by_xref(self, source, xref):
        '''
        Returns all the ChemComps that match the specified cross reference (database
        identifier) in the specified external database.
        
        Parameters
        ----------
        source : str
            Name of the database source of the cross reference, e.g.
        xref : str
            Database identifier in the external database.
        
        Returns
        -------
        xrefs : list
            ChemComps that match the specified cross reference.
        
        Examples
        --------
        >>>> ChemCompAdaptor().fetch_all_by_xref('ChEMBL Compound', 'CHEMBL941')
        [<ChemComp(STI)>]
        '''
        query = self.query.join('XRefs').filter(and_(XRef.source==source, XRef.xref==xref))
        return query.all()

    def fetch_all_by_chembl_id(self, chembl_id):
        '''
        Returns all chemical components with the same structure as the ChEMBL molecule
        with the specified CHEMBLID.
        
        Parameters
        ----------
        chembl_id : str
            ChEMBL stable identifier.
        
        Returns
        -------
        chemcomps : list
            Chemical components having the same structurea as the ChEMBL molecule
            with the specified CHEMBLID.
        '''
        return self.fetch_all_by_xref('ChEMBL Compound', chembl_id)

    def fetch_all_approved_drugs(self):
        '''
        Returns a list of all the ChemComps that are approved drugs based on the
        information provided by ChEMBL.
        
        Returns
        -------
        chemcomps : list
            All ChemComps that are approved drugs based on the information provided
            by ChEMBL.
        '''
        return self.query.filter(ChemComp.is_approved_drug==True).all()

    @requires.rdkit_catridge
    def fetch_all_by_substruct(self, smi, *expressions, **kwargs):
        '''
        Returns all Chemical Components in the PDB that have the given SMILES
        substructure.

        Parameters
        ----------
        smi : str
            SMILES string of the substructure to be used for substructure
            searching.
        *expressions : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried Entities
        ----------------
        ChemComp, ChemCompRDMol

        Returns
        -------
        chemcomps : list
            List of chemical components that have the given substructure.

        Examples
        --------
        >>> ChemCompAdaptor().fetch_all_by_substruct('c1cc(cnc1)c2ccncn2')
        [<ChemComp(AK8)>, <ChemComp(BZ9)>, <ChemComp(K11)>, <ChemComp(L1E)>,
        <ChemComp(LJE)>, <ChemComp(LJF)>, <ChemComp(MR9)>, <ChemComp(MPZ)>,
        <ChemComp(MUH)>, <ChemComp(NIL)>, <ChemComp(PRC)>, <ChemComp(PZF)>,
        <ChemComp(RAJ)>, <ChemComp(STI)>, <ChemComp(XDK)>]

        Requires
        --------
        .. important:: `RDKit  <http://www.rdkit.org>`_ PostgreSQL cartridge.
        '''
        limit = kwargs.get('limit', 100) 
        
        query = self.query.join('RDMol')
        query = query.filter(and_(ChemCompRDMol.contains(smi), *expressions))

        return query.limit(limit).all()

    @requires.rdkit_catridge
    def fetch_all_by_superstruct(self, smiles, *expressions, **kwargs):
        '''
        Returns all Chemical Components in the PDB that have the given SMILES
        superstructure.

        Parameters
        ----------
        smiles : string
            SMILES string of the superstructure to be used for superstructure
            searching.
        *expressions : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried Entities
        ----------------
        ChemComp, ChemCompRDMol

        Returns
        -------
        chemcomps : list
            List of chemical components that have the given superstructure.

        Examples
        --------
        >>> ChemCompAdaptor().fetch_all_by_superstruct('Cc1ccc(cc1Nc2nccc(n2)c3cccnc3)NC(=O)c4ccc(cc4)CN5CC[NH+](CC5)C')
        [<ChemComp(ACU)>, <ChemComp(0PY)>, <ChemComp(FOR)>, <ChemComp(NEH)>,
        <ChemComp(1MR)>, <ChemComp(271)>, <ChemComp(P1R)>, <ChemComp(3MP)>,
        <ChemComp(ARF)>, <ChemComp(ABN)>, <ChemComp(ACE)>, <ChemComp(ACM)>,
        <ChemComp(AEM)>, <ChemComp(DIS)>, <ChemComp(ANL)>, <ChemComp(BNZ)>,...]

        Requires
        --------
        .. important:: `RDKit  <http://www.rdkit.org>`_ PostgreSQL cartridge.
        '''
        limit = kwargs.get('limit', 100) 
        
        query = self.query.join('RDMol')
        query = query.filter(and_(ChemCompRDMol.contained_in(smi), *expressions))

        return query.limit(limit).all()        

    @requires.rdkit_catridge
    def fetch_all_by_smarts(self, smarts, *expressions, **kwargs):
        '''
        Returns all chemical components that match the given SMARTS pattern.

        Parameters
        ----------
        smarts : string
            The SMARTS pattern to be used for SMARTS pattern matching.

        Returns
        -------
        hits : list
            List of chemical components that match the given SMARTS pattern.

        Queried Entities
        ----------------
        ChemComp, ChemCompRDMol

        Examples
        --------
        >>> ChemCompAdaptor().fetch_all_by_smarts('[#8]=[C,N]-aaa[F,Cl,Br,I]')
        [<ChemComp(024)>, <ChemComp(136)>, <ChemComp(14A)>, <ChemComp(1RC)>,
        <ChemComp(3BZ)>, <ChemComp(33T)>, <ChemComp(33Y)>, <ChemComp(34Z)>,
        <ChemComp(35B)>, <ChemComp(394)>, <ChemComp(395)>, <ChemComp(3BE)>,...]

        Requires
        --------
        .. important:: `RDKit  <http://www.rdkit.org>`_ PostgreSQL cartridge.

        See Also
        --------
        ChemCompAdaptor.fetch_all_by_substruct
        ChemCompAdaptor.fetch_all_by_superstruct
        ChemCompAdaptor.fetch_all_by_sim
        '''
        limit = kwargs.get('limit', 100) 
        
        query = self.query.join('RDMol')
        query = query.filter(and_(ChemCompRDMol.matches(smi), *expressions))

        return query.limit(limit).all()        

    @requires.rdkit_catridge
    def fetch_all_by_sim(self, smi, *expressions, **kwargs):
        '''
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
        *expressions : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried Entities
        ----------------
        ChemComp, ChemCompRDFP

        Returns
        -------
        hits : list
            List of tuples in the form (ChemComp, similarity)

        Examples
        --------
        >>> ChemCompAdaptor().fetch_all_by_sim('Cc1ccc(cc1Nc2nccc(n2)c3cccnc3)NC(=O)c4ccc(cc4)CN5CC[NH+](CC5)C')
        [<ChemComp(STI)>, <ChemComp(MPZ)>, <ChemComp(PRC)>]

        Requires
        --------
        .. important:: `RDKit  <http://www.rdkit.org>`_ PostgreSQL cartridge.
        '''
        threshold = kwargs.get('threshold', 0.5)  
        fp = kwargs.get('fp', 'circular')  
        limit = kwargs.get('limit', 100)        
        
        if fp == 'circular':
            query = func.rdkit.morganbv_fp(smi,2).label('queryfp')
            target = ChemCompRDFP.circular_fp

        elif fp == 'torsion':
            query = func.rdkit.torsionbv_fp(smi).label('queryfp')
            target = ChemCompRDFP.torsion_fp

        elif fp == 'atompair':
            query = func.rdkit.atompairbv_fp(smi).label('queryfp')
            target = ChemCompRDFP.atompair_fp

        else:
            msg = "The fingerprint type [{0}] does not exist.".format(fp)
            raise RuntimeError(msg)

        # SET THE SIMILARITY THRESHOLD FOR THE INDEX
        session.execute(text("SET rdkit.tanimoto_threshold=:threshold").execution_options(autocommit=True).params(threshold=threshold))

        tanimoto = func.rdkit.tanimoto_sml(query, target).label('tanimoto')
        index = func.rdkit.tanimoto_sml_op(query,target)

        query = session.query(ChemComp, tanimoto).join('RDFP').filter(
            and_(index, *expressions)).order_by('tanimoto DESC')

        return query.limit(limit).all()

    def fetch_all_by_trgm_sim(self, smiles, *expressions, **kwargs):
        '''
        Returns all chemical components that are similar to the given SMILES string
        using trigam similarity (similar to LINGO).

        Parameters
        ----------
        threshold : float, default=0.6
            Similarity threshold that will be used for searching.
        limit : int, default=25
            Maximum number of hits that will be returned.

        Returns
        -------
        resultset : list
            List of tuples (ChemComp, similarity) containing the chemical components
            and the calculated trigram similarity.

        Queried Entities
        ----------------
        ChemComp

        Examples
        --------
        >>>> ChemCompAdaptor().fetch_all_by_trgm_sim('Cc1ccc(cc1Nc2nccc(n2)c3cccnc3)NC(=O)c4ccc(cc4)CN5CC[NH+](CC5)C')
        [(<ChemComp(STI)>, 0.883721), (<ChemComp(NIL)>, 0.73913),
        (<ChemComp(PRC)>, 0.738095), (<ChemComp(406)>, 0.666667),
        (<ChemComp(J07)>, 0.604167), (<ChemComp(AD5)>, 0.6),
        (<ChemComp(AAX)>, 0.6), (<ChemComp(VX6)>, 0.6)]

        Requires
        --------
        .. important:: `pg_trgm  <http://www.postgresql.org/docs/current/static/pgtrgm.html>`_ PostgreSQL extension.
        '''
        threshold = kwargs.get('threshold', 0.6)
        limit = kwargs.get('limit', 25)

        # SET THE SIMILARITY THRESHOLD FOR THE INDEX
        session.execute(text("SELECT set_limit(:threshold)").execution_options(autocommit=True).params(threshold=threshold))

        similarity = func.similarity(ChemComp.ism,smiles).label('similarity')

        query = session.query(ChemComp, similarity)
        query = query.filter(and_(ChemComp.like(smiles), *expressions))
        
        # KNN-GIST
        query = query.order_by(ChemComp.ism.op('<->')(smiles)).limit(limit)

        return query.all()

    def fetch_all_by_usr_moments(self, *expressions, **kwargs):
        '''
        Returns all Chemical Components whose conformers have an ultrafast-shape
        recognition (USR) similarity above the given threshold.

        Parameters
        ----------
        usr_space : list

        usr_moments : list
            USR moments used as a query against the chemical component conformer
            database. Must have a length of 12 or 60 if CREDO atom types
            are to be included in the similarity calculation.
        limit : int
            Number of hits that should be returned.
        max_confs : int
            Maximal number of top N conformers to consider for searching.
        ow : float, default=1.0
            Weight for the ALL atom-to-reference points distribution.
        hw : float, default=0.0
            Weight for the HYDROPHOBE atom-to-reference points distribution.
        rw : float, default=0.0
            Weight for the AROMATIC atom-to-reference points distribution.
        aw : float, default=0.0
            Weight for the ACCEPTOR atom-to-reference points distribution.
        dw : float, default=0.0
            Weight for the DONOR atom-to-reference points distribution.

        Returns
        -------
        hits : list
            List of tuples in the form (ChemComp, USR similarity)

        Queried Entities
        ----------------
        ChemComp

        Examples
        --------
        >>>> ca = ChemCompAdaptor()
        >>>> sti = ca.fetch_by_het_id('STI')
        >>>> cf = sti.Conformers[0]
        >>>> ca.fetch_all_by_usr_moments(usr_space=cf.usr_space, usr_moments=cf.usr_moments)
        [(<ChemComp(STI)>, 1.0), (<ChemComp(MPZ)>, 0.44282570958121),
        (<ChemComp(FCP)>, 0.10721552034706), (<ChemComp(406)>, 0.104637934203438),
        (<ChemComp(HDY)>, 0.0987175950862142), (<ChemComp(H8H)>, 0.098655279476252),
        (<ChemComp(I1P)>, 0.0984545212924485), (<ChemComp(571)>, 0.0978471078355951),
        (<ChemComp(UNB)>, 0.0978355469289522), (<ChemComp(BWP)>, 0.0974130374010336)]

        Notes
        -----
        Depending on the weights, the USR similarity might be above 1.0 or return
        lower values.
        '''
        usr_space = kwargs.get('usr_space')
        usr_moments = kwargs.get('usr_moments',[])

        # FACTOR BY WHICH THE USR SHAPE MOMENTS WILL BE ENLARGED IN USER SPACE
        probe_radius = kwargs.get('probe_radius', 0.5)

        # MAXIMUM NUMBER OF CHEMICAL COMPONENTS TO BE RETURNED
        limit = kwargs.get('limit', 25)

        # WEIGHTS FOR THE INDIVIDUAL ATOM TYPE MOMENTS
        ow = kwargs.get('ow', 1.0)
        hw = kwargs.get('hw', 0.25)
        rw = kwargs.get('rw', 0.25)
        aw = kwargs.get('aw', 0.25)
        dw = kwargs.get('dw', 0.25)

        # RAISE AN ERROR IF NEITHER A CUBE NOR THE USR MOMENTS HAVE BEEN PROVIDED
        if len(usr_moments) != 60: raise ValueError('The 60 USR shape descriptors are required.')

        # CREATE A PROBE AROUND THE QUERY IN USR SPACE IF NONE IS PROVIDED
        if usr_space:
            probe = func.cube_enlarge(usr_space, probe_radius, 12).label('probe')
        else:
            usr_space = func.cube(usr_moments)
            probe = func.cube_enlarge(usr_space, probe_radius, 12).label('probe')

        # CUBE DISTANCE GIST INDEX
        index = ChemCompConformer.contained_in(probe)

        # USRCAT SIMILARITY
        similarity = func.arrayxd_usrcatsim(ChemCompConformer.usr_moments, usr_moments, ow, hw, rw, aw, dw).label('similarity')

        # USRCAT SEARCH AGAINST CONFORMERS IN SUBQUERY
        subquery = session.query(ChemCompConformer.het_id, func.max(similarity).label('similarity'))
        subquery = subquery.filter(index).group_by(ChemCompConformer.het_id)
        subquery = subquery.order_by("2 DESC").limit(limit).subquery()

        # GET THE CHEMCOMP ENTITIES
        query = session.query(ChemComp, subquery.c.similarity)
        query = query.join((subquery, subquery.c.het_id==ChemComp.het_id)).filter(and_(*expressions))
        
        return query.all()

from ..models.xref import XRef
from ..models.chemcomp import ChemComp
from ..models.chemcompfragment import ChemCompFragment
from ..models.chemcompconformer import ChemCompConformer
from ..models.chemcomprdmol import ChemCompRDMol
from ..models.chemcomprdfp import ChemCompRDFP
from ..models.residue import Residue