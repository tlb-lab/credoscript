from sqlalchemy.sql.expression import and_, func

from credoscript import phenotype_to_ligand, variation_to_binding_site
from credoscript.mixins import PathAdaptorMixin
from credoscript.mixins.base import paginate

class LigandAdaptor(PathAdaptorMixin):
    """
    Adaptor to fetch ligands from CREDO with different criteria.
    """
    def __init__(self, dynamic=False, paginate=False, per_page=100, options=()):
        """
        An example for joinedload could be (Ligand.MolString, Ligand.LigandUSR).
        """
        self.query = Ligand.query
        self.dynamic = dynamic
        self.paginate = paginate
        self.per_page = per_page

        # add options to this query: can be joinedload, undefer etc.
        for option in options: self.query = self.query.options(option)

    def fetch_by_ligand_id(self, ligand_id, **kwargs):
        """
        """
        return self.query.get(ligand_id)

    @paginate
    def fetch_all_by_het_id(self, het_id, *expr, **kwargs):
        """
        """
        query = self.query.filter(and_(Ligand.ligand_name==het_id.upper(),
                                         *expr))

        return query

    @paginate
    def fetch_all_by_structure_id(self, structure_id, *expr, **kwargs):
        """
        """
        query = self.query.join('Biomolecule')
        query = query.filter(and_(Biomolecule.structure_id==structure_id, *expr))

        return query

    @paginate
    def fetch_all_in_contact_with_chain_id(self, chain_id, *expr, **kwargs):
        """
        Returns all ligands that can be found in contact with binding-site residues
        belonging to the chain with the given chain_id.
        """
        query = self.query.join(BindingSiteResidue,
                                BindingSiteResidue.ligand_id==Ligand.ligand_id)
        query = query.join(Peptide,
                           Peptide.residue_id==BindingSiteResidue.residue_id)
        query = query.filter(and_(Peptide.chain_id==chain_id, *expr))

        return query.distinct()

    @paginate
    def fetch_all_in_contact_with_residue_id(self, residue_id, *expr, **kwargs):
        """
        """
        query = self.query.join(BindingSiteResidue, BindingSiteResidue.ligand_id==Ligand.ligand_id)
        query = query.join(Peptide, Peptide.residue_id==BindingSiteResidue.residue_id)
        query = query.filter(and_(Peptide.residue_id==residue_id, *expr))

        return query.distinct()

    @paginate
    def fetch_all_in_contact_with_variation_id(self, variation_id, *expr, **kwargs):
        """
        Returns all ligands whose binding sites are in in contact with residues
        that can be linked to variations with the given variation_id.
        """
        query = self.query.join(variation_to_binding_site,
                                variation_to_binding_site.c.ligand_id==Ligand.ligand_id)
        query = query.filter(and_(variation_to_binding_site.c.variation_id==variation_id,
                                  *expr))

        return query.distinct()

    @paginate
    def fetch_all_by_phenotype_id(self, phenotype_id, *expr, **kwargs):
        """
        Returns all ligands whose binding sites contain residues that are linked
        to variations matching the given phenotype_id (from EnsEMBL).
        """
        query = self.query.join(phenotype_to_ligand,
                                phenotype_to_ligand.c.ligand_id==Ligand.ligand_id)
        query = query.filter(and_(phenotype_to_ligand.c.phenotype_id==phenotype_id,
                                  *expr))

        return query.distinct()

    @paginate
    def fetch_all_by_chembl_id(self, chembl_id, *expr, **kwargs):
        """
        Returns all ligands that contain a chemical components that can be linked
        to a ChEMBL molecule with the specified ChEMBL identifier.

        Parameters
        ----------
        chembl_id : str
            ChEMBL compound stable identifier.
        *expr : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried entities
        ----------------
        Ligand, LigandComponent, ChemComp, XRef

        Returns
        -------
        ligands : list
            ligands that contain a chemical components that can be linked to a
            ChEMBL molecule with the specified ChEMBL identifier.

        Examples
        --------
        >>> LigandAdaptor().fetch_all_by_chembl_id('CHEMBL1323')
        [<Ligand(B 301 017)>, <Ligand(D 301 017)>, <Ligand(A 302 017)>,
         <Ligand(B 401 017)>, <Ligand(A 201 017)>, <Ligand(B 203 017)>,
         <Ligand(A 201 017)>, <Ligand(B 203 017)>, <Ligand(B 401 017)>,
         <Ligand(A 402 017)>]
        """
        query = self.query.join('Components','ChemComp','XRefs')
        query = query.filter(and_(XRef.source=='ChEMBL Compound', XRef.xref==chembl_id,
                                  *expr))

        return query

    @paginate
    def fetch_all_by_uniprot(self, uniprot, *expr, **kwargs):
        """
        Returns all ligands that are in contact with a protein having the specified
        UniProt accession.

        Parameters
        ----------
        uniprot : str
            UniProt accession.
        *expr : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Joins
        -----
        Ligand, BindingSiteResidue, Peptide, XRef

        Returns
        -------
        ligands : list
            All ligands that are in contact with a protein having the specified
            UniProt accession.

        Examples
        --------
        >>> LigandAdaptor().fetch_all_by_uniprot('P03372')
        >>> [<Ligand(B 600 OHT)>, <Ligand(A 600 OHT)>,...]
        """
        query = self.query.join(BindingSiteResidue, BindingSiteResidue.ligand_id==Ligand.ligand_id)
        query = query.join(Peptide, Peptide.residue_id==BindingSiteResidue.residue_id)
        query = query.join(XRef, and_(XRef.entity_type=='Chain',
                                      XRef.entity_id==Peptide.chain_id))

        query = query.filter(and_(XRef.source=='UniProt', XRef.xref==uniprot.upper(),
                                  *expr)).distinct()

        return query

    @paginate
    def fetch_all_by_cath_dmn(self, dmn, *expr, **kwargs):
        """
        Returns all ligands that are in contact with peptides having the specified
        CATH domain identifier.

        Parameters
        ----------
        dmn : str
            CATH domain.
        *expr : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Joins
        -----
        Ligand, BindingSiteResidue, Peptide

        Returns
        -------
        ligands : list
            All ligands that are in contact with a protein having the specified
            CATH domain identifier.

        Examples
        --------
        >>> LigandAdaptor().fetch_all_by_cath_dmn('1bcuH01')
        >>> [<Ligand(H 280 PRL)>]
        """
        query = self.query.join(BindingSiteResidue, BindingSiteResidue.ligand_id==Ligand.ligand_id)
        query = query.join(Peptide, Peptide.residue_id==BindingSiteResidue.residue_id)

        query = query.filter(and_(Peptide.cath==dmn, *expr)).distinct()

        return query

    @paginate
    def fetch_all_true_fragments(self, *expr, **kwargs):
        """
        Returns all ligands that are true fragments, i.e. not derived through
        RECAP fragmentation.
        """
        query = self.query.join('ChemComp')
        query = query.filter(and_(ChemComp.is_fragment==True, *expr))

        return query

    @paginate
    def fetch_all_in_contact_with_kinases(self, *expr, **kwargs):
        """
        Returns all ligands whose binding sites are in contact with protein
        kinase chains.
        """
        query = self.query.join('BindingSite')
        query = query.filter(and_(BindingSite.is_kinase==True, *expr))

        return query

    @paginate
    def fetch_all_having_xbonds(self, *expr, **kwargs):
        """
        Returns all ligands that form halogen bonds.
        """
        query = self.query.join('LigandFragments')
        query = query.filter(and_(LigandFragment.num_xbond>0, *expr))

        return query.distinct()

    @paginate
    def fetch_all_having_metal_complexes(self, *expr, **kwargs):
        """
        Returns all ligands that form metal complexes.
        """
        query = self.query.join('LigandFragments')
        query = query.filter(and_(LigandFragment.num_metal_complex>0, *expr))

        return query.distinct()

    @paginate
    def fetch_all_most_recent(self, *expr, **kwargs):
        """
        Returns all ligands whose binding sites are in
        """
        query = self.query.join('Biomolecule','Structure')
        query = query.filter(and_(*expr))
        query = query.order_by(Structure.deposition_date.desc().nullslast())

        return query

    @paginate
    def fetch_all_by_usr_moments(self, *expr, **kwargs):
        """
        Performs an Ultrast Shape Recognition with CREDO Atom Types (USRCAT) search
        of this Ligand against all other Ligands in CREDO.

        Parameters
        ----------
        limit : int, default=25
            The number of hits that should be returned.
        probe_radius : float, default=0.5
            The radius by which the 12D USR space of the query will be expanded.
        usr_space : cube
            The 12D Cube (original USR moments).
        usr_moments : list
            60 USRCAT moments.
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
            List of tuples in the form (Ligand, USRCat similarity)

        Notes
        -----
        - Original USR behaviour can be simulated by setting the weights for
          hw, rw, aw, and dw to 0.

        References
        ----------
        Ballester, P. J. & Richards, G. W. Ultrafast shape recognition to search
        compound databases for similar molecular shapes. Journal of Computational
        Chemistry  28, 1711-1723 (2007).

        Examples
        --------
        >>>> ca = ChemCompAdaptor()
        >>>> sti = ca.fetch_by_het_id('STI')
        >>>> cf = sti.Conformers[0]
        >>>> LigandAdaptor().fetch_all_by_usr_moments(usr_space=cf.usr_space, usr_moments=cf.usr_moments, probe_radius=1.0)
        [(<Ligand(A 233 STI)>, 0.167131669359064), (<Ligand(B 1 VDN)>, 0.0675610022143043),
         (<Ligand(A 1 VDN)>, 0.0667632829909636), (<Ligand(A 1000 N3B)>, 0.0579785163927853),
         (<Ligand(A 490 VNF)>, 0.0456206050153479), (<Ligand(B 702 CPS)>, 0.041573161599066),
         (<Ligand(B 1471 140)>, 0.0334515825641013), (<Ligand(E 6178 VDY)>, 0.0326079480179413),
         (<Ligand(D 473 PAM)>, 0.0284358164031147), (<Ligand(E 1460 PLM)>, 0.0275288778074261),
         (<Ligand(D 2001 VD3)>, 0.0272922654340162), (<Ligand(A 1003 MYR)>, 0.0270479516947393)]
        """
        ligand_id = kwargs.get("ligand_id", 0)
        usr_space = kwargs.get('usr_space', [])
        usr_moments = kwargs.get('usr_moments', [])
        threshold = kwargs.get('threshold', 0.5)
        limit = kwargs.get('limit', 100)

        usr_space, usr_moments = list(usr_space), list(usr_moments)

        # get the moments from a CREDO ligand id an identifier was provided
        if ligand_id:
            ligand = self.query.get(ligand_id)

            if ligand:
                usr_space, usr_moments = ligand.usr_space, ligand.usr_moments
            else:
                raise ValueError('Ligand with ligand_id {} does not exist.'
                                 .format(ligand_id))

        # raise an error if neither a cube nor the USR moments have been provided
        if len(usr_moments) != 60:
            raise ValueError('The 60 USR shape descriptors are required.')

        # factor by which the usr shape moments will be enlarged in user space
        probe_radius = kwargs.get('probe_radius', 0.75)

        # weights for the individual atom type moments
        ow = kwargs.get('ow', 1.0)
        hw = kwargs.get('hw', 0.25)
        rw = kwargs.get('rw', 0.25)
        aw = kwargs.get('aw', 0.25)
        dw = kwargs.get('dw', 0.25)

        # create a probe around the query in USR space
        probe = func.cube_enlarge(func.cube(usr_space), probe_radius, 12).label('probe')

        # USRCAT similarity
        sim = func.arrayxd_usrcatsim(LigandUSR.usr_moments, usr_moments,
                                     ow, hw, rw, aw, dw).label('similarity')

        # cube distance GIST index
        where = and_(LigandUSR.usr_space.op('<@')(probe), sim >= threshold)

        # create a subquery with the actual USR search
        query = LigandUSR.query.filter(where).order_by("2 DESC").limit(limit)
        query = query.with_entities(LigandUSR.ligand_id, sim)
        subquery = query.subquery()

        # join in the ligands on the top hits
        query = self.query.add_column(subquery.c.similarity)
        query = query.join((subquery, subquery.c.ligand_id==Ligand.ligand_id))
        query = query.filter(and_(*expr))

        return query

    def fetch_all_by_fuzcav(self, *expr, **kwargs):
        """
        Returns the hits of a FuzCav search executed with this ligand against all
        ligands in CREDO.

        No pagination here, only top hits are interesting.

        References
        ----------


        Examples
        --------

        """
        # get the used parameters for FuzCav
        ligand_id = kwargs.get("ligand_id")
        fp = kwargs.get("fp", [])
        threshold = kwargs.get("threshold", 0.16)
        fptype = kwargs.get("fptype", "calpha")
        metric = kwargs.get("metric", "fuzcavglobal")
        limit = kwargs.get('limit', 100)

        # get the FuzCav fingerprint column corresponding to the query parameter
        if fptype == "calpha": targetfp = BindingSiteFuzcav.calphafp
        elif fptype == "rep": targetfp = BindingSiteFuzcav.repfp
        else: raise ValueError("{} is not a valid fingerprint type.".format(fptype))

        # get the (dis)similarity metric function corresponding to the query parameter
        if metric == "fuzcavglobal": simfunc = func.arrayxi_fuzcavsim_global
        elif metric == "simpson": simfunc = func.arrayxi_simpson
        elif metric == "russell-rao": simfunc = func.arrayxi_russell_rao
        elif metric == "ochiai": simfunc = func.arrayxi_ochiai
        elif metric == "kulcz": simfunc = func.arrayxi_kulcz
        else: raise ValueError("unknown metric: {}".format(metric))

        if ligand_id:
            query = BindingSiteFuzcav.query.filter(BindingSiteFuzcav.ligand_id==ligand_id)
            query = query.with_entities(targetfp)
            queryfp = query.scalar()

        # use an existing FuzCav fingerprint as query
        elif fp: queryfp = fp

        # compile the similarity function
        similarity = simfunc(targetfp, queryfp).label("similarity")

        # retrieve the top :limit hits
        hits = BindingSiteFuzcav.query.filter(similarity > threshold)
        hits = hits.with_entities(BindingSiteFuzcav.ligand_id, similarity)
        hits = hits.order_by("2 DESC").limit(limit).subquery("hits")

        # join the ligands back in
        query = self.query.add_column(hits.c.similarity)
        query = query.join(hits, hits.c.ligand_id==Ligand.ligand_id).order_by("similarity DESC")

        return query

from ..models.xref import XRef
from ..models.peptide import Peptide
from ..models.ligand import Ligand
from ..models.ligandfragment import LigandFragment
from ..models.chemcomp import ChemComp
from ..models.bindingsite import BindingSite
from ..models.biomolecule import Biomolecule
from ..models.structure import Structure
from ..models.ligandusr import LigandUSR
from ..models.bindingsiteresidue import BindingSiteResidue
from ..models.bindingsitefuzcav import BindingSiteFuzcav
