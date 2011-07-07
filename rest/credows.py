from werkzeug import Response
from sqlalchemy.util import OrderedDict

import tubes
from tubes import Application
from credo.credoscript import *

ENTITY  = '^/credo/{entity}/?$'
QUERY   = '^/credo/{entity}/({query})/?$'
TARGET  = '^/credo/{entity}/({query})/({target})/?$'
app     = Application()

'''
/structures :
    /[pdb|structure_id] : Structure with PDB or structure_id
        /biomolecules : Biological assemblies derived from this structure

/biomolecules :
    /[biomolecule_id] : Biomolecule with biomolecule_id
        /ligands
            ?
                min_hvy_atoms : Minimum number of heavy atoms
                drug_like={true} : Include only drug-like ligands

/chains :
    /[chain_id]
        /residues

        /variations
            ?
            source={dbsnp,cosmic,omim}
'''

def jsonify(obj):
    '''
    Converts an SQLAlchemy object or list of such into a dictionary that can be
    easily transformed to JSON.
    '''
    # OBJECT IS A LIST OF ENTITIES
    if isinstance(obj,list):
        meta = obj[0]._meta
        data = [item._data for item in obj]

    # OBJECT IS SINGLE ENTITY
    else:
        meta = obj._meta
        data = obj._data

    # ORDERED DICTIONARY TO MAKE SURE THAT METADATA COMES BEFORE DATA
    return OrderedDict([('metadata', meta), ('data',data)])

@app.get(ENTITY.format(entity='(\w+)[:](.+)'))
def get_entity(app, args, params):
    '''
    Returns the entity with the specified stable identifier.

    Routes
    ------
    /stable_id
    '''
    entity_type, id = map(str.upper, args)

    if entity_type == 'STRUCT':
        structure = StructureAdaptor().fetch_by_pdb(id)
        return jsonify(structure)

    else:
        msg = 'Entity type {type} does not exist.'.format(type=entity_type)
        return Response(msg, 404)

@app.get(QUERY.format(entity='ligands', query='\d+'), produces=tubes.JSON)
@app.get(TARGET.format(entity='ligands', query='\d+', target='.+'), produces=tubes.JSON)
def get_ligand(app, args, params):
    '''
    Returns a ligand or one of its mapped attributes.

    Routes
    ------
    /ligand/[ligand_id] : Ligand having the specified ligand_id
        /contacts : Contacts in the form bgn.serial, end.serial, sift
            ?
            distance=4.5 :
            secondary={true} : Defaults to 'false'
    '''
    adaptor = LigandAdaptor()

    # GET THE TWO POSSIBLE ARGUMENTS
    if len(args) == 1: ligand_id, target = args.pop(), None
    else: ligand_id, target = args

    ligand = adaptor.fetch_by_ligand_id(ligand_id)

    # LIGAND DOES NOT EXIST IN CREDO
    if not ligand: return Response('No ligand found.', 404)

    if not target: return jsonify(ligand)

    # RETURN THE INTERATOMIC CONTACTS OF THIS LIGAND
    elif target == 'contacts':

        try: distance = float(params.get('distance', 4.5))
        except ValueError: return Response('Invalid float argument: {distance}.'.format(distance=distance), 400)

        # STORE USER-DEFINED EXPRESSIONS THAT WILL BE USED FOR QUERYING LATER
        expressions = [Contact.distance<=distance]

        # EXCLUDE SECONDARY CONTACTS BY DEFAULT
        if not params.get('secondary'): expressions.append(Contact.is_secondary==False)

        contacts = ligand.get_contacts(*expressions)

        return jsonify(contacts, container='contacts')

    # RETURN 404 IF MAPPING FOR SPECIFIED TARGET DOES NOT EXIST
    else: return Response('Filter {target} does not exist.'.format(target=target), 404)

@app.get(QUERY.format(entity='chemcomps', query='\w{2,3}'), produces=tubes.JSON)
@app.get(TARGET.format(entity='chemcomps', query='\w{2,3}', target='.+'), produces=tubes.JSON)
def get_chem_comp(app, args, params):
    '''
    Returns a single chemical component or its mapped attributes.

    Routes
    ------
    /chemcomps/[het_id] : Chemical component with the specified het_id
        /fragments : All fragments of the chemical component
            ?
            shared={true,false} : Only shared fragments
            terminal={true,false} : Only terminal fragments
        /ligandcomponents :
        /ligands : All ligands containing this chemical component
    '''
    ca = ChemCompAdaptor()

    # GET THE TWO POSSIBLE ARGUMENTS: HET-ID AND NAME OF TARGET MAPPING
    if len(args) == 1: het_id, target = args.pop(), None
    else: het_id, target = args

    het_id = het_id.upper()

    # FETCH THE SPECIFIED CHEMICAL COMPONENT
    chemcomp = ca.fetch_by_het_id(het_id.upper())

    # RETURN SINGLE CHEMICAL COMPONENT IF NO OTHER ATTRIBUTE WAS GIVEN
    if not target: return jsonify(chemcomp)

    elif target == 'ligandcomponents':
        pass

    # RETURN ALL LIGANDS OF THIS CHEMICAL COMPONENT
    elif target == 'ligands':
        ligands = LigandAdaptor().fetch_all_by_het_id(het_id)

        if ligands: return jsonify(ligands)
        else: return Response('No ligands found.', 404)

    # GET THE FRAGMENTS OF THE CHEMICAL COMPONENT
    elif target == 'fragments':
        fragments = chemcomp.get_fragments()

        if fragments:
            return jsonify(fragments)
        else:
            msg = 'No fragments found for chemical components {het_id}.'.format(het_id=het_id)
            return Response(msg, 404)

    elif target == 'xrefs':
        xrefs = chemcomp.get_xrefs()

        if xrefs:
            return jsonify(xrefs)
        else:
            msg = 'No cross references found for chemical components {het_id}.'.format(het_id=het_id)
            return Response(msg, 404)

    # RETURN 404 IF MAPPING FOR SPECIFIED TARGET DOES NOT EXIST
    else: return Response('Filter {target} does not exist.'.format(target=target), 404)

@app.get(ENTITY.format(entity='chemcomps'), produces=tubes.JSON)
def get_chem_comps(app, args, params):
    '''
    Returns chemical components.

    Routes
    ------
    /chemcomps : All chemical components
        ?
        substruct=SMILES : Chemical components having the specified substructure
        superstruct=SMILES : Chemical components having the specified superstructure
        pattern=SMARTS : Chemical components matching the specified SMARTS pattern
        similarity=SMILES : Chemical components similar to specified query
            &
            threshold=0.5
            fp={'circular','path','torsion'}
        *
        druglike={true,false} : Only drug-like not drug-like chemical components
    '''
    chemcomps = []

    if not params:

        # RETURN ALL CHEMICAL COMPONENTS
        chemcomps = session.query(ChemComp).all()

    else:
        ca = ChemCompAdaptor()

        # STORE USER-DEFINED EXPRESSIONS THAT WILL BE USED FOR QUERYING LATER
        expressions = []

        # BY DEFAULT, PARAMETER VALUES ARE LISTS
        for key,value in params.items(): params[key] = value[0]

        # CHEMICAL COMPONENT EXPRESSIONS

        # DRUG-LIKENESS
        if 'druglike' in params:
            if params['druglike'] == 'true': IS_DRUG_LIKE=True
            else: IS_DRUG_LIKE=False

            expressions.append(ChemComp.is_drug_like==IS_DRUG_LIKE)

        # ONLY STANDARD ATOMS
        if 'stdatoms' in params:
            if params['stdatoms'] == 'true': HAS_STD_ATOMS=True
            else: HAS_STD_ATOMS=False

            expressions.append(ChemComp.has_std_atoms==HAS_STD_ATOMS)

        # CHEMICAL PATTERN MATCHING AND SIMILARITY SEARCHING
        if 'substruct' in params:
            smi = params['substruct']
            chemcomps = ca.fetch_all_by_substruct(smi, *expressions)

        elif 'superstruct' in params:
            smi = params['superstruct']
            chemcomps = ca.fetch_all_by_superstruct(smi, *expressions)

        elif 'pattern' in params:
            sma = params['pattern']
            chemcomps = ca.fetch_all_by_smarts(sma, *expressions)

        elif 'similarity' in params:
            smi = params['similarity']

            threshold = params.get('threshold', 0.5)
            fp = params.get('fp', 'circular')

            # METHOD RETURNS TUPLES IN THE FORM (CHEMCOMP, TANIMOTO)
            hits = ca.fetch_all_by_sim(smi,threshold,fp, *expressions)
            chemcomps = [chemcomp for chemcomp, sim in hits]

        else: return Response('Specified filter does not exist.', 404)

    if not chemcomps: return Response('Nothing found.', 404)

    # RETURN A DICTIONARY THAT WILL BE MARSHALLED TO JSON
    else: return jsonify(chemcomps)

# START THE SERVER
tubes.run(app, reload=True, debug=True)

