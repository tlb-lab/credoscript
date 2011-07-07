from sqlalchemy.sql.expression import and_, func

from ..meta import session, binding_sites, ligand_usr

class LigandAdaptor(object):
    '''
    '''
    def __init__(self):
        '''
        '''
        self.query = session.query(Ligand)

    def fetch_by_ligand_id(self, ligand_id):
        '''
        '''
        return self.query.get(ligand_id)

    def fetch_all_by_het_id(self, het_id, *expressions):
        '''
        '''
        return self.query.filter(and_(Ligand.ligand_name==het_id, *expressions)).all()

    def fetch_all_by_structure_id(self, structure_id, *expressions):
        '''
        '''
        return self.query.join('Biomolecule').filter(
            and_(Biomolecule.structure_id==structure_id, *expressions)).all()

    def fetch_all_by_uniprot(self, uniprot, *expressions):
        '''
        Returns all ligands that are in contact with a protein having the specified
        UniProt accession.

        Parameters
        ----------
        uniprot : str
            UniProt accession.
        *expressions : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Joins
        -----
        Ligand, binding_sites, Residue, XRef

        Returns
        -------
        ligands : list
            All ligands that are in contact with a protein having the specified
            UniProt accession.

        Examples
        --------
        >>> LigandAdaptor().fetch_all_by_uniprot('P03372')
        >>> [<Ligand(B 600 OHT)>, <Ligand(A 600 OHT)>,...]
        '''
        query = self.query.join(
            (binding_sites, binding_sites.c.ligand_id==Ligand.ligand_id),
            (Residue, Residue.residue_id==binding_sites.c.residue_id),
            (XRef, and_(XRef.entity=='Chain', XRef.entity_id==Residue.chain_id)))

        query = query.filter(and_(XRef.source=='UniProt',
                                  XRef.xref==uniprot,
                                  *expressions))

        return query.all()

    def fetch_all_by_cath_dmn(self, dmn, *expressions):
        '''
        Returns all ligands that are in contact with peptides having the specified
        CATH domain identifier.

        Parameters
        ----------
        dmn : str
            CATH domain.
        *expressions : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Joins
        -----
        Ligand, binding_sites, Peptide, ResMap

        Returns
        -------
        ligands : list
            All ligands that are in contact with a protein having the specified
            CATH domain identifier.

        Examples
        --------
        >>> LigandAdaptor().fetch_all_by_cath_dmn('1bcuH01')
        >>> [<Ligand(H 280 PRL)>]
        '''
        query = self.query.join(
            (binding_sites, binding_sites.c.ligand_id==Ligand.ligand_id),
            (Peptide, Peptide.residue_id==binding_sites.c.residue_id),
            (ResMap, ResMap.res_map_id==Peptide.res_map_id))

        query = query.filter(and_(ResMap.cath==dmn, *expressions))

        return query.all()

    def fetch_all_by_usr_moments(self, *expressions, **kwargs):
        '''
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
        '''
        usr_space = kwargs.get('usr_space',[])
        usr_moments = kwargs.get('usr_moments',[])

        # RAISE AN ERROR IF NEITHER A CUBE NOR THE USR MOMENTS HAVE BEEN PROVIDED
        if len(usr_moments) != 60: raise ValueError('The 60 USR shape descriptors are required.')

        # FACTOR BY WHICH THE USR SHAPE MOMENTS WILL BE ENLARGED IN USER SPACE
        probe_radius = kwargs.get('probe_radius', 0.5)

        # MAXIMUM NUMBER OF HITS TO BE RETURNED
        limit = kwargs.get('limit', 25)

        # WEIGHTS FOR THE INDIVIDUAL ATOM TYPE MOMENTS
        ow = kwargs.get('ow', 1.0)
        hw = kwargs.get('hw', 0.25)
        rw = kwargs.get('rw', 0.25)
        aw = kwargs.get('aw', 0.25)
        dw = kwargs.get('dw', 0.25)

        # CREATE A PROBE AROUND THE QUERY IN USR SPACE
        probe = func.cube_enlarge(usr_space, probe_radius, 12).label('probe')

        # CUBE DISTANCE GIST INDEX
        index = ligand_usr.c.usr_space.op('<@')(probe)

        # USRCAT SIMILARITY
        similarity = func.arrayxd_usrcatsim(ligand_usr.c.usr_moments, usr_moments, ow, hw, rw, aw, dw).label('similarity')

        subquery = session.query(ligand_usr.c.ligand_id, similarity)
        subquery = subquery.filter(index).order_by("2 DESC").limit(limit).subquery()

        ligands = session.query(Ligand, subquery.c.similarity)
        ligands = ligands.join((subquery, subquery.c.ligand_id==Ligand.ligand_id))
        ligands = ligands.filter(and_(*expressions))

        return ligands.all()

from ..models.xref import XRef
from ..models.resmap import ResMap
from ..models.peptide import Peptide
from ..models.residue import Residue
from ..models.ligand import Ligand