import os
import sys
import json

from sqlalchemy.sql.expression import and_, func
from sqlalchemy.orm import backref, composite, deferred, mapper, relationship, column_property
from sqlalchemy.orm.collections import column_mapped_collection

from .models import *
from .adaptors import *
from .meta import *
from .support.interactiontypes import *

mapper(ResMap, metadata.tables['pdb.res_map'])

if HAS_RDKIT_CARTRIDGE:
    mapper(ChemCompRDMol, metadata.tables['pdbchem.chem_comp_rdmols'],
           exclude_properties=['rdmol'],
           properties={
            'rdmol': column_property(func.rdkit.mol_send(metadata.tables['pdbchem.chem_comp_rdmols'].c.rdmol))
           })
    mapper(ChemCompRDFP, metadata.tables['pdbchem.chem_comp_rdfps'])

# FRAGMENTS
mapper(ChemCompFragment, metadata.tables['pdbchem.chem_comp_fragments'])
mapper(FragmentHierarchy, metadata.tables['pdbchem.fragment_hierarchies'])

mapper(Fragment, metadata.tables['pdbchem.fragments'],
       properties={
        'ChemCompFragments': relationship(ChemCompFragment,
                                          primaryjoin=ChemCompFragment.fragment_id==metadata.tables['pdbchem.fragments'].c.fragment_id,
                                          foreign_keys = [ChemCompFragment.fragment_id],
                                          uselist=True, innerjoin=True,
                                          backref=backref('Fragment', uselist=False))
        })

mapper(Hetatm, metadata.tables['credo.hetatms'])
mapper(Atom, metadata.tables['credo.atoms'])
mapper(XRef, metadata.tables['credo.xrefs'])

mapper(LigandFragment, metadata.tables['credo.ligand_fragments'],
       properties={
        'Fragment': relationship(Fragment,
                                 primaryjoin=Fragment.fragment_id==metadata.tables['credo.ligand_fragments'].c.fragment_id,
                                 foreign_keys = [Fragment.fragment_id],
                                 uselist=False, innerjoin=True,
                                 backref=backref('LigandFragments',uselist=True, innerjoin=True)
                                 ),
        'Atoms': relationship(Atom,
                              secondary = metadata.tables['credo.ligand_fragment_atoms'],
                              primaryjoin = metadata.tables['credo.ligand_fragments'].c.ligand_fragment_id==metadata.tables['credo.ligand_fragment_atoms'].c.ligand_fragment_id,
                              secondaryjoin = metadata.tables['credo.ligand_fragment_atoms'].c.atom_id==Atom.atom_id,
                              foreign_keys = [metadata.tables['credo.ligand_fragment_atoms'].c.ligand_fragment_id,
                                              metadata.tables['credo.ligand_fragment_atoms'].c.atom_id],
                              uselist=True, innerjoin=True)
        }
       )

# TABLES FROM THE CHEMICAL COMPONENT SPACE
mapper(ChemCompConformer, metadata.tables['pdbchem.chem_comp_conformers'])

chemcompmapper = mapper(ChemComp, metadata.tables['pdbchem.chem_comps'],
       properties={
        'ChemCompFragments': relationship(ChemCompFragment,
                                          primaryjoin=ChemCompFragment.het_id==metadata.tables['pdbchem.chem_comps'].c.het_id,
                                          foreign_keys = [ChemCompFragment.het_id],
                                          uselist=True, innerjoin=True,
                                          backref=backref('ChemComp', uselist=False, innerjoin=True)),
        'Fragments': relationship(Fragment,
                                  secondary=metadata.tables['pdbchem.chem_comp_fragments'],
                                  primaryjoin=metadata.tables['pdbchem.chem_comps'].c.het_id==ChemCompFragment.het_id,
                                  secondaryjoin=metadata.tables['pdbchem.chem_comp_fragments'].c.fragment_id==Fragment.fragment_id,
                                  foreign_keys=[metadata.tables['pdbchem.chem_comp_fragments'].c.het_id, Fragment.fragment_id],
                                  uselist=True, innerjoin=True,
                                  backref = backref('ChemComps', uselist=True, innerjoin=True)
                                  ),
        'Conformers': relationship(ChemCompConformer,
                                   primaryjoin=ChemCompConformer.het_id==metadata.tables['pdbchem.chem_comps'].c.het_id,
                                   foreign_keys = [ChemCompConformer.het_id],
                                   uselist=True, innerjoin=True,
                                   backref=backref('ChemComp', uselist=False, innerjoin=True)
                                   ),
        'XRefs': relationship(XRef, collection_class=column_mapped_collection(XRef.source),
                              primaryjoin=and_(XRef.entity_type=='ChemComp', XRef.entity_id==metadata.tables['pdbchem.chem_comps'].c.chem_comp_id),
                              foreign_keys=[XRef.entity_type, XRef.entity_id], uselist=True, innerjoin=True)
        })

# ADD THE RDMOL PROPERTY ONLY IF RDKIT IS INSTALLED
if HAS_RDKIT:
    chemcompmapper.add_properties(
        {
            'RDMol': relationship(ChemCompRDMol,
                                  primaryjoin=ChemCompRDMol.het_id==metadata.tables['pdbchem.chem_comps'].c.het_id,
                                  foreign_keys=[ChemCompRDMol.het_id], uselist=False, innerjoin=True,
                                  backref=backref('ChemComp', uselist=False, innerjoin=True)),
            'RDFP': relationship(ChemCompRDFP,
                                 primaryjoin=ChemCompRDFP.het_id==metadata.tables['pdbchem.chem_comps'].c.het_id,
                                 foreign_keys=[ChemCompRDFP.het_id], uselist=False, innerjoin=True,
                                 backref=backref('ChemComp', uselist=False, innerjoin=True))
        })

mapper(ProtFragment, metadata.tables['credo.prot_fragments'])

mapper(Contact, metadata.tables['credo.contacts'],
       properties={
        'AtomBgn': relationship(Atom,
                                primaryjoin=and_(Atom.atom_id==metadata.tables['credo.contacts'].c.atom_bgn_id,
                                                 Atom.biomolecule_id==metadata.tables['credo.contacts'].c.biomolecule_id), # PARTITION CONSTRAINT-EXCLUSION
                                foreign_keys=[Atom.atom_id, Atom.biomolecule_id], uselist=False, innerjoin=True),
        'AtomEnd': relationship(Atom,
                                primaryjoin=and_(Atom.atom_id==metadata.tables['credo.contacts'].c.atom_end_id,
                                                 Atom.biomolecule_id==metadata.tables['credo.contacts'].c.biomolecule_id), # PARTITION CONSTRAINT-EXCLUSION
                                foreign_keys=[Atom.atom_id, Atom.biomolecule_id], uselist=False, innerjoin=True)
        })

mapper(AromaticRing, metadata.tables['credo.aromatic_rings'])

mapper(AtomRingInteraction, metadata.tables['credo.atom_ring_interactions'],
       properties={
        'Atom': relationship(Atom,
                             primaryjoin=Atom.atom_id==metadata.tables['credo.atom_ring_interactions'].c.atom_id,
                             foreign_keys = [Atom.atom_id], uselist=False, innerjoin=True),
        'AromaticRing': relationship(AromaticRing,
                                     primaryjoin=AromaticRing.aromatic_ring_id==metadata.tables['credo.atom_ring_interactions'].c.aromatic_ring_id,
                                     foreign_keys = [AromaticRing.aromatic_ring_id], uselist=False, innerjoin=True,
                                     backref=backref('AtomRingInteractions', uselist=True, innerjoin=True))
        }
       )

mapper(RingInteraction, metadata.tables['credo.ring_interactions'],
       properties = {
        'AromaticRingBgn': relationship(AromaticRing,
                                        primaryjoin=AromaticRing.aromatic_ring_id==metadata.tables['credo.ring_interactions'].c.aromatic_ring_bgn_id,
                                        foreign_keys=[AromaticRing.aromatic_ring_id], uselist=False, innerjoin=True),
        'AromaticRingEnd': relationship(AromaticRing,
                                        primaryjoin=AromaticRing.aromatic_ring_id==metadata.tables['credo.ring_interactions'].c.aromatic_ring_end_id,
                                        foreign_keys=[AromaticRing.aromatic_ring_id], uselist=False, innerjoin=True),
        'ClosestAtomBgn': relationship(Atom,
                                       primaryjoin=Atom.atom_id==metadata.tables['credo.ring_interactions'].c.closest_atom_bgn_id,
                                       foreign_keys = [Atom.atom_id], uselist=False, innerjoin=True),
        'ClosestAtomEnd': relationship(Atom,
                                       primaryjoin=Atom.atom_id==metadata.tables['credo.ring_interactions'].c.closest_atom_end_id,
                                       foreign_keys = [Atom.atom_id], uselist=False, innerjoin=True),
        }
       )

mapper(Residue, metadata.tables['credo.residues'],
       properties={
        'Atoms': relationship(Atom,
                              primaryjoin=and_(Atom.residue_id==metadata.tables['credo.residues'].c.residue_id,
                                               Atom.biomolecule_id==metadata.tables['credo.residues'].c.biomolecule_id), # PARTITION CONSTRAINT-EXCLUSION
                              foreign_keys = [Atom.residue_id, Atom.biomolecule_id], uselist=True, innerjoin=True,
                              collection_class=column_mapped_collection((Atom.atom_name, Atom.alt_loc)),
                              backref=backref('Residue', uselist=False, innerjoin=True)),
        'AromaticRings': relationship(AromaticRing,
                                      primaryjoin=AromaticRing.residue_id==metadata.tables['credo.residues'].c.residue_id,
                                      foreign_keys = [AromaticRing.residue_id], uselist=True, innerjoin=True,
                                      backref=backref('Residue', uselist=False, innerjoin=True)),
       })

mapper(Peptide, metadata.tables['credo.peptides'],
       properties={
        'Residue': relationship(Residue,
                                primaryjoin=Residue.residue_id==metadata.tables['credo.peptides'].c.residue_id,
                                foreign_keys=[Residue.residue_id], uselist=False, innerjoin=True,
                                backref=backref('Peptide', uselist=False, innerjoin=True)),
        'Atoms': relationship(Atom,
                              collection_class=column_mapped_collection((Atom.atom_name, Atom.alt_loc)),
                              primaryjoin=Atom.residue_id==metadata.tables['credo.peptides'].c.residue_id,
                              foreign_keys = [Atom.residue_id], uselist=True, innerjoin=True),
        'AromaticRings': relationship(AromaticRing,
                                      primaryjoin=AromaticRing.residue_id==metadata.tables['credo.peptides'].c.residue_id,
                                      foreign_keys = [AromaticRing.residue_id], uselist=True, innerjoin=True),
        'ResMap': relationship(ResMap,
                               primaryjoin=ResMap.res_map_id==metadata.tables['credo.peptides'].c.res_map_id,
                               foreign_keys = [ResMap.res_map_id], uselist=False, innerjoin=True),
        'ProtFragment': relationship(ProtFragment,
                                     secondary = metadata.tables['credo.prot_fragment_residues'],
                                     primaryjoin=metadata.tables['credo.peptides'].c.residue_id==metadata.tables['credo.prot_fragment_residues'].c.residue_id,
                                     secondaryjoin=metadata.tables['credo.prot_fragment_residues'].c.prot_fragment_id==metadata.tables['credo.prot_fragments'].c.prot_fragment_id,
                                     foreign_keys = [metadata.tables['credo.prot_fragment_residues'].c.residue_id,
                                                     metadata.tables['credo.prot_fragment_residues'].c.prot_fragment_id], uselist=False, innerjoin=True,
                                     backref = backref('Peptides', uselist=True, innerjoin=True)
                                     )
        })

mapper(Nucleotide, metadata.tables['credo.nucleotides'],
       properties={
        'Residue': relationship(Residue,
                                primaryjoin=Residue.residue_id==metadata.tables['credo.nucleotides'].c.residue_id,
                                foreign_keys=[Residue.residue_id], uselist=False, innerjoin=True,
                                backref=backref('Nucleotide', uselist=False, innerjoin=True)),
        })

mapper(Saccharide, metadata.tables['credo.saccharides'],
       properties={
        'Residue': relationship(Residue,
                                primaryjoin=Residue.residue_id==metadata.tables['credo.saccharides'].c.residue_id,
                                foreign_keys=[Residue.residue_id], uselist=False, innerjoin=True,
                                backref=backref('Saccharide', uselist=False, innerjoin=True)),
        })

mapper(LigandComponent, metadata.tables['credo.ligand_components'],
       properties={
        'Atoms': relationship(Atom,
                              collection_class=column_mapped_collection(Atom.atom_name),
                              primaryjoin = Atom.residue_id==metadata.tables['credo.ligand_components'].c.residue_id,
                              foreign_keys = [Atom.residue_id], innerjoin=True, uselist=True),
        'Residue': relationship(Residue,
                                primaryjoin=Residue.residue_id==metadata.tables['credo.ligand_components'].c.residue_id,
                                foreign_keys=[Residue.residue_id], uselist=False, innerjoin=True),
        'ChemComp': relationship(ChemComp,
                                 secondary=metadata.tables['credo.residues'],
                                 primaryjoin=metadata.tables['credo.ligand_components'].c.residue_id==metadata.tables['credo.residues'].c.residue_id,
                                 secondaryjoin=metadata.tables['credo.residues'].c.res_name==ChemComp.het_id,
                                 foreign_keys=[metadata.tables['credo.residues'].c.residue_id,metadata.tables['credo.residues'].c.res_name],
                                 uselist=False, innerjoin=True,
                                 backref=backref('LigandComponents', uselist=True, innerjoin=True)),
        'LigandFragments': relationship(LigandFragment,
                                        primaryjoin=LigandFragment.ligand_component_id==metadata.tables['credo.ligand_components'].c.ligand_component_id,
                                        foreign_keys = [LigandFragment.ligand_component_id], uselist=True, innerjoin=True,
                                        backref=backref('LigandComponent', uselist=False, innerjoin=True))
        }
       )

mapper(LigandUSR, metadata.tables['credo.ligand_usr'])

mapper(LigandMolString, metadata.tables['credo.ligand_molstrings'],
       properties={
        'pdb': deferred(metadata.tables['credo.ligand_molstrings'].c.pdb),
        'oeb': deferred(metadata.tables['credo.ligand_molstrings'].c.oeb),
    })

mapper(Ligand, metadata.tables['credo.ligands'],
       properties={
        'Components': relationship(LigandComponent,
                                      primaryjoin=LigandComponent.ligand_id==metadata.tables['credo.ligands'].c.ligand_id,
                                      foreign_keys=[LigandComponent.ligand_id], uselist=True, innerjoin=True,
                                      backref=backref('Ligand', uselist=False, innerjoin=True)),
        'LigandFragments': relationship(LigandFragment,
                                        primaryjoin=LigandFragment.ligand_id==metadata.tables['credo.ligands'].c.ligand_id,
                                        foreign_keys = [LigandFragment.ligand_id], uselist=True, innerjoin=True,
                                        backref=backref('Ligand', uselist=False, innerjoin=True)),
        'XRefs': relationship(XRef, collection_class=column_mapped_collection(XRef.source),
                              primaryjoin=and_(XRef.entity_type=='Ligand', XRef.entity_id==metadata.tables['credo.ligands'].c.ligand_id),
                              foreign_keys=[XRef.entity_type, XRef.entity_id], uselist=True, innerjoin=True),
        'MolString': relationship(LigandMolString,
                                  primaryjoin=LigandMolString.ligand_id==metadata.tables['credo.ligands'].c.ligand_id,
                                  foreign_keys=[LigandMolString.ligand_id], uselist=False, innerjoin=True,
                                  backref=backref('Ligand', uselist=False, innerjoin=True)),
        'name': metadata.tables['credo.ligands'].c.ligand_name
        })

mapper(Chain, metadata.tables['credo.chains'],
       properties={
        'Residues': relationship(Residue,
                                 collection_class=column_mapped_collection((Residue.res_num, Residue.ins_code)),
                                 primaryjoin=Residue.chain_id==metadata.tables['credo.chains'].c.chain_id,
                                 foreign_keys=[Residue.chain_id], uselist=True, innerjoin=True,
                                 backref=backref('Chain', uselist=False, innerjoin=True)),
        'Peptides': relationship(Peptide,
                                 collection_class=column_mapped_collection((Peptide.res_num, Peptide.ins_code)),
                                 primaryjoin=Peptide.chain_id==metadata.tables['credo.chains'].c.chain_id,
                                 foreign_keys=[Peptide.chain_id], uselist=True, innerjoin=True,
                                 backref=backref('Chain', uselist=False, innerjoin=True)),
        'ProtFragments': relationship(ProtFragment,
                                      primaryjoin=ProtFragment.chain_id==metadata.tables['credo.chains'].c.chain_id,
                                      foreign_keys=[ProtFragment.chain_id], uselist=True, innerjoin=True,
                                      backref=backref('Chain', uselist=False, innerjoin=True)),
        'XRefs': relationship(XRef, collection_class=column_mapped_collection(XRef.source),
                              primaryjoin=and_(XRef.entity_type=='Chain', XRef.entity_id==metadata.tables['credo.chains'].c.chain_id),
                              foreign_keys=[XRef.entity_type, XRef.entity_id], uselist=True, innerjoin=True),
        'seq': deferred(metadata.tables['credo.chains'].c.chain_seq),
        'title': deferred(metadata.tables['credo.chains'].c.title)
       }
       )

mapper(Groove, metadata.tables['credo.grooves'],
       properties={
        'ChainProt': relationship(Chain,
                                  primaryjoin=Chain.chain_id==metadata.tables['credo.grooves'].c.chain_prot_id,
                                  foreign_keys=[Chain.chain_id], uselist=False, innerjoin=True),
        'ChainNuc': relationship(Chain,
                                 primaryjoin=Chain.chain_id==metadata.tables['credo.grooves'].c.chain_nuc_id,
                                 foreign_keys=[Chain.chain_id], uselist=False, innerjoin=True),
       })

mapper(Interface, metadata.tables['credo.interfaces'],
       properties={
        'ChainBgn': relationship(Chain,
                                 primaryjoin=Chain.chain_id==metadata.tables['credo.interfaces'].c.chain_bgn_id,
                                 foreign_keys=[Chain.chain_id], uselist=False, innerjoin=True),
        'ChainEnd': relationship(Chain,
                                 primaryjoin=Chain.chain_id==metadata.tables['credo.interfaces'].c.chain_end_id,
                                 foreign_keys=[Chain.chain_id], uselist=False, innerjoin=True),
       })

mapper(Biomolecule, metadata.tables['credo.biomolecules'],
       properties={
        'Chains': relationship(Chain,
                               collection_class=column_mapped_collection(Chain.pdb_chain_id),
                               primaryjoin=Chain.biomolecule_id==metadata.tables['credo.biomolecules'].c.biomolecule_id,
                               foreign_keys=[Chain.biomolecule_id], uselist=True, innerjoin=True,
                               backref=backref('Biomolecule', uselist=False, innerjoin=True)),
        'Interfaces': relationship(Interface,
                                   primaryjoin=Interface.biomolecule_id==metadata.tables['credo.biomolecules'].c.biomolecule_id,
                                   foreign_keys=[Interface.biomolecule_id], uselist=True, innerjoin=True,
                                   backref=backref('Biomolecule', uselist=False, innerjoin=True)),
        'Grooves': relationship(Groove,
                                primaryjoin=Groove.biomolecule_id==metadata.tables['credo.biomolecules'].c.biomolecule_id,
                                foreign_keys=[Groove.biomolecule_id], uselist=True, innerjoin=True,
                                backref=backref('Biomolecule', uselist=False, innerjoin=True)),
        'Ligands': relationship(Ligand,
                                primaryjoin=Ligand.biomolecule_id==metadata.tables['credo.biomolecules'].c.biomolecule_id,
                                foreign_keys=[Ligand.biomolecule_id], uselist=True, innerjoin=True,
                                backref=backref('Biomolecule', uselist=False, innerjoin=True)),
        'AromaticRings': relationship(AromaticRing,
                                      primaryjoin=AromaticRing.biomolecule_id==metadata.tables['credo.biomolecules'].c.biomolecule_id,
                                      foreign_keys=[AromaticRing.biomolecule_id], uselist=True, innerjoin=True,
                                      backref=backref('Biomolecule', uselist=False, innerjoin=True)),
        'Atoms': relationship(Atom,
                              primaryjoin=Atom.biomolecule_id==metadata.tables['credo.biomolecules'].c.biomolecule_id,
                              foreign_keys=[Atom.biomolecule_id], uselist=True, innerjoin=True,
                              backref=backref('Biomolecule', uselist=False, innerjoin=True)),
       })

mapper(Structure, metadata.tables['credo.structures'],
       properties={
        'Biomolecules': relationship(Biomolecule,
                                     collection_class=column_mapped_collection(Biomolecule.assembly_serial),
                                     primaryjoin=Biomolecule.structure_id==metadata.tables['credo.structures'].c.structure_id,
                                     foreign_keys=[Biomolecule.structure_id], uselist=True, innerjoin=True,
                                     backref=backref('Structure', uselist=False, innerjoin=True)),
        'XRefs': relationship(XRef, collection_class=column_mapped_collection(XRef.source),
                              primaryjoin=and_(XRef.entity_type=='Structure', XRef.entity_id==metadata.tables['credo.structures'].c.structure_id),
                              foreign_keys=[XRef.entity_type, XRef.entity_id], uselist=True, innerjoin=True),
        'title': deferred(metadata.tables['credo.structures'].c.title),
        'authors': deferred(metadata.tables['credo.structures'].c.authors)
       })