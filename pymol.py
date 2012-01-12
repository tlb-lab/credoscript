import os
from warnings import warn
from itertools import combinations

from sqlalchemy.orm import joinedload_all
from sqlalchemy.sql.expression import and_

from . import config
from .models import *
from .adaptors import *
from .support.pymolviewer import PyMOLViewer

PDB_DIR = config['directory']['pdb']

TYPES   = ('hbond','weakhbond','xbond','ionic','metalcomplex',
           'aromatic','hydrophobic','carbonyl')

pymol = PyMOLViewer()

def defer_update(function):
    '''
    Decorator to defer PyMOL updates of a function. Should be the last decorator.
    '''
    def wrapper(self, *args, **kwargs):
        '''
        '''
        # DO NOT UPDATE PYMOL IMMEDIATELY
        pymol.set('defer_update', 1)

        # RUN THE FUNCTION THAT IS GOING TO BE WRAPPED
        function(self, *args, **kwargs)

        # UPDATE PYMOL NOW
        pymol.set('defer_update', 0)

    return wrapper

def show_nucleotides(*args, **kwargs):
    '''
    Creates a cartoon representation for RNA/DNA and puts the selection in a
    separate group.
    '''
    group = kwargs.get('group')

    pymol.select('NUCLEOTIDES', 'resn {0}'.format('+'.join(config['residues']['nucleotides'])))

    # REMOVE SELECTION IF EMPTY
    if not pymol.count_atoms('NUCLEOTIDES'):
        pymol.delete('NUCLEOTIDES')

    else:
        pymol.show('cartoon', 'NUCLEOTIDES')
        pymol.hide('lines', 'NUCLEOTIDES')
        pymol.disable('NUCLEOTIDES')

        if group: pymol.group(group, 'NUCLEOTIDES')

def show_non_std_res(*args, **kwargs):
    '''
    '''
    group = kwargs.get('group')

    # SELECT ALL POLYMER RESIDUES THAT ARE NOT DNA AND NOT STANDARD AMINO ACIDS
    pymol.select('NON-STD-RES', 'polymer and not resn {0} and not resn {1}'.format('+'.join(config['residues']['peptides']),
                                                                                   '+'.join(config['residues']['nucleotides'])))

    if not pymol.count_atoms('NON-STD-RES'):
        pymol.delete('NON-STD-RES')

    else:
        pymol.color(config['pymol']['colors']['non-std-res'], 'NON-STD-RES and (symbol c)')
        pymol.disable('NON-STD-RES')

        if group: pymol.group(group, 'NON-STD-RES')

@defer_update
def show_disordered_regions(self, *args, **kwargs):
    '''
    Visualises disordered regions inside protein chains by connecting the residues
    flanking those regions with PyMOL distance objects.
    '''
    for chain in self.Chains.values():
        for region in chain.get_disordered_regions():
            
            # GET THE RESIDUES FLANKING THE DISORDERED REGION
            rbgn, rend = chain[region.region_start-1], chain[region.region_end+1]

            # FLANKING RESIDUES CANNOT BE OBTAINED / MOST LIKELY N- OR C-TERMINAL REGIONS
            if not rbgn or not rend:
                msg = "Could not obtain the residues flanking region {0}-{1}".format(region.region_start, region.region_end)
                warn(msg, UserWarning)
                
                continue
        
            try:
                # CREATE A DASHED LINE TO VISUALISE THE DISORDERD REGION
                pymol.distance('disordered_regions', rbgn['CA'].pymolstring, rend['CA'].pymolstring)
                pymol.color(config['pymol']['dashcolor']['disordered_region'], 'disordered_regions')
                
                # ALSO COLOR THE CA ATOMS OF THE FLANKING RESIDUES
                pymol.color(config['pymol']['dashcolor']['disordered_region'], rbgn['CA'].pymolstring)
                pymol.color(config['pymol']['dashcolor']['disordered_region'], rend['CA'].pymolstring)
                
                # REMOVE THE DISTANCE LABELS
                pymol.hide('labels', 'disordered_regions')
                
            except KeyError:
                raise KeyError('one of the residues is missing the CA atom.')

@defer_update
def load_biomolecule(self, *args, **kwargs):
    '''
    Load a PDB structure into PyMOL
    '''
    pdb = self.Structure.pdb
    assembly_serial = self.assembly_serial

    # STRING USED TO REPRESENT BIOMOLECULE IN PYMOL
    string_id = '{0}-{1}'.format(pdb, assembly_serial)

    # LOOK FOR STRUCTURE ON LOCAL MIRROR
    path = os.path.join(PDB_DIR, '{0}.pdb'.format(string_id))

    if os.path.exists(path): pymol.load(path, string_id)
    else: raise IOError('the structure cannot be found: {0}'.format(path))

    # SHOW PROTEIN AS CARTOON WITH SIDE CHAINS
    pymol.show('cartoon')
    pymol.set('cartoon_side_chain_helper', 1)

    group = 'BIOMOL-{0}'.format(string_id)

    pymol.group(group, string_id)

    # COLOR ALL CARBONS GREY
    pymol.color(config['pymol']['colors']['carbon'],'(symbol c)')

    # CREATE CENTROIDS OF AROMATIC RINGS
    if kwargs.get('show_rings'):
        for ring in self.AromaticRings:
            ring.show(obj=string_id, normal=True, group=group)

    # SHOW LIGANDS AS STICKS INCLUDING CENTROIDS
    for ligand in self.Ligands: ligand.show(group=group)

    # REMOVE WATER MOLECULES FROM PYMOL (DEFAULT FALSE)
    if kwargs.get('hide_water', False): pymol.hide('everything','resn HOH')

    # HIGHLIGHT MODIFIED RESIDUES
    if kwargs.get('non_std_res', True): show_non_std_res(group=group)

    # SHOW DNA AS CARTOON
    show_nucleotides(group=group)

    pymol.orient(string_id)

def show_ligand(self, **kwargs):
    '''
    '''
    show = kwargs.get('show', 'sticks')
    color = kwargs.get('color', 'grey70')
    group = kwargs.get('group')

    if self.num_hvy_atoms > 1:
        pymol.select(self.ligand_id, self.pymolstring)
        pymol.show(show, self.ligand_id)
        pymol.color(color, '(symbol c) and {0}'.format(self.ligand_id))

    else:
        pymol.select(self.ligand_id, self.pymolstring)
        pymol.show('spheres', self.pymolstring)

    # CREATE LIGAND GROUP
    pymol.group('LIGAND-{0}'.format(self.ligand_id), self.ligand_id)

    # ADD LIGAND GROUP TO STRUCTURE GROUP
    pymol.group(group, 'LIGAND-{0}'.format(self.ligand_id))

    pymol.disable(self.ligand_id)

def show_aromatic_ring(self, **kwargs):
    '''
    Uses a pseudoatom to represent the centroid of the aromatic ring.
    '''
    color = kwargs.get('color', 'grey70')
    group = kwargs.get('group')
    obj = kwargs.get('obj', '') # SHOULD BE PDB CODE

    coords = map(float, self.Centroid)
    cname = 'CX{0}'.format(self.ring_number)

    chain = self.Residue.Chain.pdb_chain_id
    res_num = self.Residue.res_num
    res_name = self.Residue.res_name
    ins_code = self.Residue.ins_code.strip()

    pymol.pseudoatom(obj, pos=coords, name=cname, chain=chain, res_num=str(res_num)+ins_code,
                     res_name=res_name, color=color, vdw=0.5)

    pymol.hide('everything', self.pymolstring)
    pymol.show('sphere', self.pymolstring)

    # SHOW THE RING NORMAL
    if kwargs.get('normal'):
        normal = map(float, self.Normal + self.Centroid)
        nname = 'NX{0}'.format(self.ring_number)
        nselect = '{0}/{1}'.format(self.Residue.pymolstring, nname)
        label = '{0}-NORMALS'.format(self.Biomolecule.biomolecule_id)

        # CREATE A PSEUDONATOM TO REPRESENT THE TIP OF THE RING NORMAL
        pymol.pseudoatom(obj, pos=normal, name=nname, chain=chain,
                         res_num=str(res_num)+ins_code, res_name=res_name,
                         color=color, vdw=0.0)


        pymol.distance(label, self.pymolstring, nselect)

        # HIDE THE DISTANCE LABEL
        pymol.hide('labels', label)

        # FORMAT NORMAL
        pymol.color(config['pymol']['dashcolor']['normal'], label)
        pymol.set('dash_radius', config['pymol']['dashradius']['normal'], label)
        pymol.set('dash_gap', config['pymol']['dashgap']['normal'], label)
        pymol.set('dash_length', config['pymol']['dashlength']['normal'], label)

        # HIDE THE PSEUDOATOMS LINES OF THE NORMAL POSITION
        pymol.hide('everything', nselect)

        # ADD NORMALS OF THIS BIOMOLECULE TO BIOMOL GROUP
        if group: pymol.group(group, label)

@defer_update
def show_contacts(self, *expressions, **kwargs):
    '''
    Visualises all interatomic contacts of this entity with other entities through
    colour-coded PyMOL distance objects.

    Parameters
    ----------
    labels : bool (default=False)
        Boolean flag indicating whether distance labels should be kept.
    distance_cut_off : float (default=4.5)
        Maximum allowed distance for inter-atomic contacts.
    water_bridges : bool (default=True)

    Examples
    --------
    >>>

    '''
    # GET THE CLASS NAME OF THE OBJECT THE FUNCTION IS ATTACHED TO
    credo_class = self.__class__.__name__

    # GET THE PRIMARY KEY OF THE ENTITY
    credo_id = self._entity_id

    labels = kwargs.get('labels', False)

    contacts = self.Contacts.options(joinedload_all(Contact.AtomBgn, Contact.AtomEnd, innerjoin=True))
  
    contacts = contacts.filter(and_(*expressions)).all()

    # ALSO INCLUDE BRIDGED HBONDS
    if kwargs.get('water_bridges', False):
        for water in self.get_proximal_water():
    
            # KEEP ONLY THOSE BRIDGES THAT ARE WITHIN THE MAXIMUM DISTANCE OF 6.05 ANGSTROM
            for wc1, wc2 in combinations(water.Contacts,2):
                if wc1.distance + wc2.distance <= 6.1:
                    contacts.extend([wc1,wc2])

    # TURN INTO SET TO AVOID DUPLICATES WITH WATER CONTACTS
    contacts = set(contacts)

    # KEEP TRACK OF INTERACTION TYPES THAT ARE PRESENT IN THIS PROTEIN-LIGAND COMPLEX
    used_interaction_types = set()

    for contact in contacts:
        interactions = []

        # DISTANCE FLAG
        if contact.is_covalent: DIST_FLAG = 'covalent'
        elif contact.is_vdw_clash: DIST_FLAG = 'vdwclash'
        elif contact.is_vdw: DIST_FLAG = 'vdw'
        elif contact.is_proximal: DIST_FLAG = 'proximal'

        sift = contact.sift[4:]

        if not any(sift):
            interactions.append(('undefined', DIST_FLAG))

        # ADD ALL INTERACTIONS FOR THIS PAIR
        else:
            interactions.extend(((contact_type, DIST_FLAG) for contact_type,s in zip(TYPES,sift) if s))

        # DRAW THE DISTANCE IN PYMOL
        for contact_type, flag in interactions:

            # CREATE DISTANCE OBJECT IN PYMOL BETWEEN THE TWO ATOMS
            pymol.distance('{0}-{1}-{2}'.format(credo_id, contact_type, flag),
                           contact.AtomBgn.pymolstring, contact.AtomEnd.pymolstring)

            # KEEP TRACK OF USED INTERACTION TYPES
            used_interaction_types.add((contact_type, flag))

    # UPDATE ONLY EXISTING TYPES TO PREVENT AN ERROR IN PYMOL
    for contact_type, flag in used_interaction_types:
        label = '{0}-{1}-{2}'.format(credo_id, contact_type, flag)

        # UPDATE THE VISUALISATION OF THE INTERACTION TYPES
        pymol.color(config['pymol']['dashcolor'][contact_type][flag], label)
        pymol.set('dash_radius', config['pymol']['dashradius'][contact_type][flag], label)
        pymol.set('dash_gap', config['pymol']['dashgap'][contact_type][flag], label)
        pymol.set('dash_length', config['pymol']['dashlength'][contact_type][flag], label)

        interaction_group = '{0}-{1}'.format(credo_id, contact_type.upper())

        pymol.group(interaction_group, '{0}-{1}-*'.format(credo_id, contact_type))
        pymol.group('{0}-{1}'.format(credo_class.upper(), credo_id), interaction_group)

        # REMOVE THE DISTANCE LABELS
        if not labels: pymol.hide('labels', label)

    # ORDER OBJECTS
    pymol.order('*')

@defer_update
def highlight_secondary_contacts(self, *args, **kwargs):
    '''
    Visualises all interatomic contacts of this entity with other entities through
    colour-coded PyMOL distance objects.

    Parameters
    ----------
    labels : bool (default=False)
        Boolean flag indicating whether distance labels should be kept.
    distance_cut_off : float (default=4.5)
        Maximum allowed distance for inter-atomic contacts.
    secondary_contacts : bool (default=True)
        Boolean flag indicating whether secondary contacts should be ignored or
        not (EXPERIMENTAL). The default value will show all possible contacts.
    water_bridges : bool (default=True)

    Examples
    --------
    >>>

    '''
    # GET THE CLASS NAME OF THE OBJECT THE FUNCTION IS ATTACHED TO
    credo_class = self.__class__.__name__

    # EXPLOIT THE FACT THAT THE HASH FUNCTION FOR EACH ENTITY IS OVERLOADED TO RETURN THE PRIMARY KEY
    credo_id = self._entity_id

    labels = kwargs.get('labels', True)
    distance_cut_off = kwargs.get('distance_cut_off', 5.0)

    # GET ALL CONTACTS WITHIN DISTANCE CUTOFF
    contacts = self.get_contacts(Contact.distance<=distance_cut_off)

    # ALSO INCLUDE BRIDGED HBONDS
    if kwargs.get('water_bridges', True):
        for water in self.get_proximal_water():

            # KEEP ONLY THOSE BRIDGES THAT ARE WITHIN THE MAXIMUM DISTANCE OF 6.05 ANGSTROM
            for wc1, wc2 in combinations(water.Contacts,2):
                if wc1.distance + wc2.distance <= 6.1:
                    contacts.extend([wc1,wc2])

    # TURN INTO SET TO AVOID DUPLICATES WITH WATER CONTACTS
    contacts = set(contacts)

    # KEEP TRACK OF INTERACTION TYPES THAT ARE PRESENT IN THIS PROTEIN-LIGAND COMPLEX
    used_interaction_types = set()

    for contact in contacts:
        interactions = []

        # DISTANCE FLAG
        if contact.is_covalent: DIST_FLAG = 'covalent'
        elif contact.is_vdw_clash: DIST_FLAG = 'vdwclash'
        elif contact.is_vdw: DIST_FLAG = 'vdw'
        elif contact.is_proximal: DIST_FLAG = 'proximal'

        if contact.is_secondary:
            pymol.distance('{0}-{1}'.format(credo_id, 'SECONDARY'),
                           contact.AtomBgn.pymolstring, contact.AtomEnd.pymolstring)
        else:
            pymol.distance('{0}-{1}'.format(credo_id, 'PRIMARY'),
                           contact.AtomBgn.pymolstring, contact.AtomEnd.pymolstring)

    if '{0}-{1}'.format(credo_id, 'PRIMARY') in pymol.get_names():
        pymol.color('grey50', '{0}-{1}'.format(credo_id, 'PRIMARY'))
    if '{0}-{1}'.format(credo_id, 'SECONDARY') in pymol.get_names():
        pymol.color('red', '{0}-{1}'.format(credo_id, 'SECONDARY'))

    # REMOVE THE DISTANCE LABELS
    if not labels: pymol.hide('labels', label)

    # ORDER OBJECTS
    pymol.order('*')

@defer_update
def show_ring_interactions(self, *args, **kwargs):
    '''
    '''
    # GET THE CLASS NAME OF THE OBJECT THE FUNCTION IS ATTACHED TO
    credo_class = self.__class__.__name__

    # EXPLOIT THE FACT THAT THE HASH FUNCTION FOR EACH ENTITY IS OVERLOADED TO RETURN THE PRIMARY KEY
    credo_id = self._entity_id

    labels = kwargs.get('labels', True)
    group = kwargs.get('group', '{0}-{1}'.format(credo_class.upper(), credo_id))

    # GET THE RING INTERACTIONS OF THIS OBJECT
    if hasattr(self, 'RingInteractions'):
        ring_interactions = self.RingInteractions
    elif hasattr(self, 'get_ring_interactions'):
        ring_interactions = self.get_ring_interactions(RingInteraction.closest_atom_distance<=4.5)
    else:
        raise RuntimeError('Entity {entity} does not have aromatic ring interactions associated with it.'.format(entity=credo_class))

    for ringint in ring_interactions:
        bgn, end = ringint.AromaticRingBgn, ringint.AromaticRingEnd

        label = 'RINGINT-{ringint.interaction_type}-{ringint.ring_interaction_id}'.format(ringint=ringint)
        pymol.distance(label, bgn.pymolstring, end.pymolstring)

        pymol.color(config['pymol']['dashcolor']['aromatic']['vdw'], label)
        pymol.set('dash_radius', '0.08', label)

        # HIDE THE TEXT LABELS
        if not labels: pymol.hide('labels', label)

        pymol.group(group, label)

@defer_update
def show_atom_ring_interactions(self, *args, **kwargs):
    '''
    '''
    # GET THE CLASS NAME OF THE OBJECT THE FUNCTION IS ATTACHED TO
    credo_class = self.__class__.__name__

    # EXPLOIT THE FACT THAT THE HASH FUNCTION FOR EACH ENTITY IS OVERLOADED TO RETURN THE PRIMARY KEY
    credo_id = self._entity_id

    labels = kwargs.get('labels', True)
    group = kwargs.get('group', '{0}-{1}'.format(credo_class.upper(), credo_id))

    # GET THE RING INTERACTIONS OF THIS OBJECT
    if hasattr(self, 'AtomRingInteractions'):
        atom_ring_interactions = self.AtomRingInteractions
    elif hasattr(self, 'get_atom_ring_interactions'):
        atom_ring_interactions = self.get_atom_ring_interactions()
    else:
        raise RuntimeError('Entity {entity} does not have atom-ring interactions associated with it.'.format(entity=credo_class))

    for atomringint in atom_ring_interactions:
        atom, aromaticring, interaction_type = atomringint.Atom, atomringint.AromaticRing, atomringint.interaction_type

        label = 'ATOMRINGINT-{atomringint.interaction_type}-{atomringint.atom_ring_interaction_id}'.format(atomringint=atomringint)
        pymol.distance(label, atom.pymolstring, aromaticring.pymolstring)

        # COLOR THE INTERACTION BASED ON TYPE
        if atomringint.interaction_type == 'CARBONPI': color = config['pymol']['dashcolor']['weakhbond']['vdw']
        elif atomringint.interaction_type == 'HALOGENPI': color = config['pymol']['dashcolor']['weakhbond']['vdw']
        elif atomringint.interaction_type == 'DONORPI': color = config['pymol']['dashcolor']['hbond']['vdw']
        elif atomringint.interaction_type == 'CATIONPI': color = config['pymol']['dashcolor']['ionic']['vdw']
        else: color = config['pymol']['dashcolor']['undefined']['vdw']

        pymol.color(color, label)
        pymol.set('dash_radius', '0.08', label)

        # HIDE THE TEXT LABEL
        if not labels: pymol.hide('labels', label)

        pymol.group(group, label)

Biomolecule.load = load_biomolecule
Biomolecule.show_disordered_regions = show_disordered_regions
Ligand.show = show_ligand
AromaticRing.show = show_aromatic_ring

# CONTACT VISUALISATION
Ligand.show_contacts = show_contacts
Residue.show_contacts = show_contacts
Atom.show_contacts = show_contacts
Interface.show_contacts = show_contacts
Groove.show_contacts = show_contacts

# RING-RING INTERACTION VISUALISATION
Ligand.show_ring_interactions = show_ring_interactions
Residue.show_ring_interactions = show_ring_interactions

# ATOM-AROMATIC RING INTERACTIONS
Ligand.show_atom_ring_interactions = show_atom_ring_interactions
AtomRingInteraction.show = show_atom_ring_interactions

Ligand.highlight_secondary_contacts = highlight_secondary_contacts