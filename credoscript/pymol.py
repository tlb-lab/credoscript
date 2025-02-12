import os
from warnings import warn
from itertools import combinations

from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import and_

from credoscript import config
from credoscript.models import *
from credoscript.adaptors import *
from credoscript.support.pymolviewer import PyMOLViewer

PDB_DIR = config['directory']['pdb']

TYPES   = ('hbond','weakhbond','xbond','ionic','metalcomplex',
           'aromatic','hydrophobic','carbonyl')

pymol = PyMOLViewer()

def defer_update(function):
    """
    Decorator to defer PyMOL updates of a function. Should be the last decorator.
    """
    def wrapper(self, *args, **kwargs):
        """
        """
        # DO NOT UPDATE PYMOL IMMEDIATELY
        pymol.set('defer_update', 1)

        # RUN THE FUNCTION THAT IS GOING TO BE WRAPPED
        function(self, *args, **kwargs)

        # UPDATE PYMOL NOW
        pymol.set('defer_update', 0)

    return wrapper

def show_nucleotides(*args, **kwargs):
    """
    Creates a cartoon representation for RNA/DNA and puts the selection in a
    separate group.
    """
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
    """
    """
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
    """
    Visualises disordered regions inside protein chains by connecting the residues
    flanking those regions with PyMOL distance objects.
    """
    for chain in self.Chains.all():
        for region in chain.disordered_regions():

            # GET THE RESIDUES FLANKING THE DISORDERED REGION
            rbgn, rend = chain[region.region_start-1], chain[region.region_end+1]

            # FLANKING RESIDUES CANNOT BE OBTAINED / MOST LIKELY N- OR C-TERMINAL REGIONS
            if not rbgn or not rend:
                warn("Could not obtain the residues flanking region {0}-{1}."
                     .format(region.region_start, region.region_end),
                     UserWarning)

                continue

            try:
                # CREATE A DASHED LINE TO VISUALISE THE DISORDERD REGION
                pymol.distance('disordered_regions', rbgn['CA'].pymolstring,
                               rend['CA'].pymolstring)
                pymol.color(config['pymol']['dashcolor']['disordered_region'],
                            'disordered_regions')

                # ALSO COLOR THE CA ATOMS OF THE FLANKING RESIDUES
                pymol.color(config['pymol']['dashcolor']['disordered_region'],
                            rbgn['CA'].pymolstring)
                pymol.color(config['pymol']['dashcolor']['disordered_region'],
                            rend['CA'].pymolstring)

                # REMOVE THE DISTANCE LABELS
                pymol.hide('labels', 'disordered_regions')

            except KeyError:
                raise KeyError('one of the residues is missing the CA atom.')

@defer_update
def load_biomolecule(self, *args, **kwargs):
    """
    Load a PDB structure into PyMOL
    """
    pdb = self.Structure.pdb
    assembly_serial = self.assembly_serial

    # string used to represent biomolecule in PyMOL
    string_id = '{0}-{1}'.format(pdb.lower(), assembly_serial)

    # look for structure on local mirror
    path = os.path.join(PDB_DIR, pdb.lower()[1:3], pdb.lower(),
                        '{0}.pdb'.format(string_id))

    if os.path.isfile(path): pymol.load(path, string_id)
    else: raise IOError('the structure cannot be found: {0}'.format(path))

    # show protein as cartoon with side chains
    pymol.show('cartoon')
    pymol.set('cartoon_side_chain_helper', 1)

    group = 'BIOMOL-{0}'.format(string_id)

    pymol.group(group, string_id)

    # color all carbons grey
    pymol.color(config['pymol']['colors']['carbon'],'(symbol c)')

    # create centroids of aromatic rings
    if kwargs.get('show_rings'):
        for ring in self.AromaticRings.all():
            ring.show(obj=string_id, normal=True, group=group)

    # show ligands as sticks including centroids
    for ligand in self.Ligands.all():
        ligand.show(group=group)

    # remove water molecules from pymol (default false)
    if kwargs.get('hide_water', False):
        pymol.hide('everything','resn HOH')

    # highlight modified residues
    if kwargs.get('non_std_res', True):
        show_non_std_res(group=group)

    # show dna as cartoon
    show_nucleotides(group=group)

    pymol.orient(string_id)

def show_ligand(self, **kwargs):
    """
    """
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

    # create ligand group
    pymol.group('LIGAND-{0}'.format(self.ligand_id), self.ligand_id)

    # add ligand group to structure group
    pymol.group(group, 'LIGAND-{0}'.format(self.ligand_id))

    pymol.disable(self.ligand_id)

def show_aromatic_ring(self, **kwargs):
    """
    Uses a pseudoatom to represent the centroid of the aromatic ring.
    """
    color = kwargs.get('color', 'grey70')
    group = kwargs.get('group')
    obj = kwargs.get('obj', '') # should be pdb code

    coords = map(float, self.Centroid)

    # name of the pseudoatom / also last part of aromatic ring path
    cname = 'AR{0}'.format(self.ring_number)

    # the residue details for the new pseudoatom
    chain = self.Residue.Chain.pdb_chain_id
    res_num = self.Residue.res_num
    res_name = self.Residue.res_name
    ins_code = self.Residue.ins_code.strip()

    # create the centroid with the residue details
    pymol.pseudoatom(obj, pos=coords, name=cname, chain=chain,
                     res_num=str(res_num)+ins_code, res_name=res_name,
                     color=color, vdw=0.5)

    pymol.hide('everything', self.pymolstring)
    pymol.show('sphere', self.pymolstring)

    # show the ring normal
    if kwargs.get('normal'):
        normal = map(float, self.Normal + self.Centroid)
        nname = 'NX{0}'.format(self.ring_number)
        nselect = '{0}/{1}'.format(self.Residue.pymolstring, nname)
        label = '{0}-NORMALS'.format(self.Biomolecule.biomolecule_id)

        # create a pseudonatom to represent the tip of the ring normal
        pymol.pseudoatom(obj, pos=normal, name=nname, chain=chain,
                         res_num=str(res_num)+ins_code, res_name=res_name,
                         color=color, vdw=0.0)

        # create a line between the centroid and the end of the normal
        pymol.distance(label, self.pymolstring, nselect)

        # hide the distance label
        pymol.hide('labels', label)

        # format normal
        pymol.color(config['pymol']['dashcolor']['normal'], label)
        pymol.set('dash_radius', config['pymol']['dashradius']['normal'], label)
        pymol.set('dash_gap', config['pymol']['dashgap']['normal'], label)
        pymol.set('dash_length', config['pymol']['dashlength']['normal'], label)

        # hide the pseudoatoms lines of the normal position
        pymol.hide('everything', nselect)

        # add normals of this biomolecule to biomol group
        if group: pymol.group(group, label)

@defer_update
def show_contacts(self, *expr, **kwargs):
    """
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

    """
    labels = kwargs.get('labels', False)

    # get the class name of the object the function is attached to
    credo_class = self.__class__.__name__

    # get the primary key of the entity
    credo_id = self._entity_id

    # fetch all the contacts for this entity
    contacts = self.Contacts.filter(and_(*expr)).all()

    # also include bridged hbonds
    if kwargs.get('water_bridges', False):
        for water in self.ProximalWater.all():

            # keep only those bridges that are within the maximum distance
            # of 6.05 angstrom
            for wc1, wc2 in combinations(water.Contacts, 2):
                if wc1.distance + wc2.distance <= 6.1:
                    contacts.extend([wc1,wc2])

    # turn into set to avoid duplicates with water contacts
    contacts = set(contacts)

    # keep track of interaction types that are present
    used_interaction_types = set()

    for contact in contacts:
        interactions = []

        # distance flag
        if contact.is_covalent: DIST_FLAG = 'covalent'
        elif contact.is_vdw_clash: DIST_FLAG = 'vdwclash'
        elif contact.is_vdw: DIST_FLAG = 'vdw'
        elif contact.is_proximal: DIST_FLAG = 'proximal'

        # feature interactions
        sift = contact.sift[5:]

        if not any(sift):
            interactions.append(('undefined', DIST_FLAG))

        # add all interactions for this pair
        else:
            interactions.extend(((contact_type, DIST_FLAG)
                                 for contact_type,s in zip(TYPES,sift) if s))

        # draw the distance in pymol
        for contact_type, flag in interactions:

            # create distance object in pymol between the two atoms
            pymol.distance('{0}-{1}-{2}'.format(credo_id, contact_type, flag),
                           contact.AtomBgn.pymolstring, contact.AtomEnd.pymolstring)

            # keep track of used interaction types
            used_interaction_types.add((contact_type, flag))

    # update only existing types to prevent an error in pymol
    for contact_type, flag in used_interaction_types:
        label = '{0}-{1}-{2}'.format(credo_id, contact_type, flag)

        # update the visualisation of the interaction types
        pymol.color(config['pymol']['dashcolor'][contact_type][flag], label)
        pymol.set('dash_radius', config['pymol']['dashradius'][contact_type][flag], label)
        pymol.set('dash_gap', config['pymol']['dashgap'][contact_type][flag], label)
        pymol.set('dash_length', config['pymol']['dashlength'][contact_type][flag], label)

        # remove the distance labels
        if not labels: pymol.hide('labels', label)

    # group the contacts by type and add the groups to the ligand group
    for contact_type in set(zip(*used_interaction_types)[0]):
        interaction_group = '{0}-{1}'.format(credo_id, contact_type.upper())
        pymol.group(interaction_group, '{0}-{1}-*'.format(credo_id, contact_type))
        pymol.group('{0}-{1}'.format(credo_class.upper(), credo_id), interaction_group)

    # order objects
    pymol.order('*')

@defer_update
def highlight_secondary_contacts(self, *args, **kwargs):
    """
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

    """
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
    """
    """
    # get the class name of the object the function is attached to
    credo_class = self.__class__.__name__

    # exploit the fact that the hash function for each entity is overloaded to
    # return the primary key
    credo_id = self._entity_id

    labels = kwargs.get('labels', True)
    group = kwargs.get('group', '{0}-{1}'.format(credo_class.upper(), credo_id))

    # get the ring interactions of this object
    if hasattr(self, 'RingInteractions'):
        ring_interactions = self.RingInteractions
    else:
        raise RuntimeError("Entity {entity} does not have aromatic ring "
                           "interactions associated with it."
                           .format(entity=credo_class))

    for ringint in ring_interactions:
        bgn, end = ringint.AromaticRingBgn, ringint.AromaticRingEnd

        label = 'RINGINT-{ringint.interaction_type}-{ringint.ring_interaction_id}'.format(ringint=ringint)
        pymol.distance(label, bgn.pymolstring, end.pymolstring)

        pymol.color(config['pymol']['dashcolor']['aromatic']['vdw'], label)
        pymol.set('dash_radius', '0.08', label)

        # hide the text labels
        if not labels: pymol.hide('labels', label)

        pymol.group(group, label)

@defer_update
def show_atom_ring_interactions(self, *expr, **kwargs):
    """
    The ring centroids have to be added first.
    """
    labels = kwargs.get('labels', True)

    # get the class name of the object the function is attached to
    credo_class = self.__class__.__name__

    # exploit the fact that the hash function for each entity is overloaded to
    # return the primary key
    credo_id = self._entity_id

    group = kwargs.get('group', '{0}-{1}'.format(credo_class.upper(), credo_id))

    # get the ring interactions of this object
    if hasattr(self, 'AtomRingInteractions'):
        atom_ring_interactions = self.AtomRingInteractions.filter(and_(*expr)).all()
    else:
        raise RuntimeError("Entity {entity} does not have atom-ring interactions "
                           "associated with it.".format(entity=credo_class))

    for atomringint in atom_ring_interactions:
        atom = atomringint.Atom
        aromaticring = atomringint.AromaticRing
        interaction_type = atomringint.interaction_type if atomringint.interaction_type else 'UNDEF'

        label = 'ATOMRINGINT-{atomringint.interaction_type}-{atomringint.atom_ring_interaction_id}'.format(atomringint=atomringint)
        pymol.distance(label, atom.pymolstring, aromaticring.pymolstring)

        # color the interaction based on type
        if atomringint.interaction_type == 'CARBONPI':
            color = config['pymol']['dashcolor']['weakhbond']['vdw']
        elif atomringint.interaction_type == 'HALOGENPI':
            color = config['pymol']['dashcolor']['xbond']['vdw']
        elif atomringint.interaction_type == 'DONORPI':
            color = config['pymol']['dashcolor']['hbond']['vdw']
        elif atomringint.interaction_type == 'CATIONPI':
            color = config['pymol']['dashcolor']['ionic']['vdw']
        else:
            color = config['pymol']['dashcolor']['undefined']['vdw']

        pymol.color(color, label)
        pymol.set('dash_radius', '0.08', label)

        # hide the text label
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