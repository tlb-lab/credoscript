import os
import sys
import json

from sqlalchemy import select
from sqlalchemy.sql.expression import and_, func
from sqlalchemy.orm import backref, composite, deferred, mapper, relationship, column_property
from sqlalchemy.orm.collections import column_mapped_collection

from .models import *
from .adaptors import *
from .meta import *
from .support.interactiontypes import *

mapper(ResMap, credo.tables['pdb.res_map'])

if HAS_RDKIT_CARTRIDGE:
    mapper(ChemCompRDMol, credo.tables['pdbchem.chem_comp_rdmols'],
           exclude_properties=['rdmol'],
           properties={
            'rdmol': column_property(func.rdkit.mol_send(credo.tables['pdbchem.chem_comp_rdmols'].c.rdmol))
           })
    mapper(ChemCompRDFP, credo.tables['pdbchem.chem_comp_rdfps'])

# FRAGMENTS
mapper(ChemCompFragment, credo.tables['pdbchem.chem_comp_fragments'])
mapper(FragmentHierarchy, credo.tables['pdbchem.fragment_hierarchies'])

mapper(Fragment, credo.tables['pdbchem.fragments'],
       properties={
        'ChemCompFragments': relationship(ChemCompFragment,
                                          primaryjoin=ChemCompFragment.fragment_id==credo.tables['pdbchem.fragments'].c.fragment_id,
                                          foreign_keys = [ChemCompFragment.fragment_id],
                                          uselist=True, innerjoin=True,
                                          backref=backref('Fragment', uselist=False))
        })

mapper(Hetatm, credo.tables['credo.hetatms'])
mapper(Atom, credo.tables['credo.atoms'])
mapper(XRef, credo.tables['credo.xrefs'])

mapper(LigandFragment, credo.tables['credo.ligand_fragments'],
       properties={
        'Fragment': relationship(Fragment,
                                 primaryjoin=Fragment.fragment_id==credo.tables['credo.ligand_fragments'].c.fragment_id,
                                 foreign_keys = [Fragment.fragment_id],
                                 uselist=False, innerjoin=True,
                                 backref=backref('LigandFragments',uselist=True, innerjoin=True)
                                 ),
        'Atoms': relationship(Atom,
                              secondary = credo.tables['credo.ligand_fragment_atoms'],
                              primaryjoin = credo.tables['credo.ligand_fragments'].c.ligand_fragment_id==credo.tables['credo.ligand_fragment_atoms'].c.ligand_fragment_id,
                              secondaryjoin = credo.tables['credo.ligand_fragment_atoms'].c.atom_id==Atom.atom_id,
                              foreign_keys = [credo.tables['credo.ligand_fragment_atoms'].c.ligand_fragment_id,
                                              credo.tables['credo.ligand_fragment_atoms'].c.atom_id],
                              uselist=True, innerjoin=True)
        }
       )

# TABLES FROM THE CHEMICAL COMPONENT SPACE
mapper(ChemCompConformer, credo.tables['pdbchem.chem_comp_conformers'])

chemcompmapper = mapper(ChemComp, credo.tables['pdbchem.chem_comps'],
       properties={
        'ChemCompFragments': relationship(ChemCompFragment,
                                      primaryjoin=ChemCompFragment.het_id==credo.tables['pdbchem.chem_comps'].c.het_id,
                                      foreign_keys = [ChemCompFragment.het_id],
                                      uselist=True, innerjoin=True,
                                      backref=backref('ChemComp', uselist=False, innerjoin=True)
                                   ),
        'Fragments': relationship(Fragment,
                                  secondary=credo.tables['pdbchem.chem_comp_fragments'],
                                  primaryjoin=credo.tables['pdbchem.chem_comps'].c.het_id==ChemCompFragment.het_id,
                                  secondaryjoin=credo.tables['pdbchem.chem_comp_fragments'].c.fragment_id==Fragment.fragment_id,
                                  foreign_keys=[credo.tables['pdbchem.chem_comp_fragments'].c.het_id, Fragment.fragment_id],
                                  uselist=True, innerjoin=True,
                                  backref = backref('ChemComps', uselist=True, innerjoin=True)
                                  ),
        'Conformers': relationship(ChemCompConformer,
                                   primaryjoin=ChemCompConformer.het_id==credo.tables['pdbchem.chem_comps'].c.het_id,
                                   foreign_keys = [ChemCompConformer.het_id],
                                   uselist=True, innerjoin=True,
                                   backref=backref('ChemComp', uselist=False, innerjoin=True)
                                   ),
        'XRefs': relationship(XRef,
                              primaryjoin=and_(XRef.entity_type=='ChemComp', XRef.entity_id==credo.tables['pdbchem.chem_comps'].c.chem_comp_id),
                              foreign_keys=[XRef.entity_type, XRef.entity_id], uselist=True, innerjoin=True)
        })

# ADD THE RDMOL PROPERTY ONLY IF RDKIT IS INSTALLED
if HAS_RDKIT:
    chemcompmapper.add_properties(
        {
            'RDMol': relationship(ChemCompRDMol,
                                  primaryjoin=ChemCompRDMol.het_id==credo.tables['pdbchem.chem_comps'].c.het_id,
                                  foreign_keys=[ChemCompRDMol.het_id], uselist=False, innerjoin=True,
                                  backref=backref('ChemComp', uselist=False, innerjoin=True)),
            'RDFP': relationship(ChemCompRDFP,
                                 primaryjoin=ChemCompRDFP.het_id==credo.tables['pdbchem.chem_comps'].c.het_id,
                                 foreign_keys=[ChemCompRDFP.het_id], uselist=False, innerjoin=True,
                                 backref=backref('ChemComp', uselist=False, innerjoin=True))
        })

mapper(ProtFragment, credo.tables['credo.prot_fragments'])

mapper(Groove, credo.tables['credo.grooves'])

mapper(Contact, credo.tables['credo.contacts'],
       properties={
        'AtomBgn': relationship(Atom,
                                primaryjoin=Atom.atom_id==credo.tables['credo.contacts'].c.atom_bgn_id,
                                foreign_keys=[Atom.atom_id], uselist=False, innerjoin=True),
        'AtomEnd': relationship(Atom,
                                primaryjoin=Atom.atom_id==credo.tables['credo.contacts'].c.atom_end_id,
                                foreign_keys=[Atom.atom_id], uselist=False, innerjoin=True)
        }
       )

mapper(AromaticRing, credo.tables['credo.aromatic_rings'])

mapper(AtomRingInteraction, credo.tables['credo.atom_ring_interactions'],
       properties={
        'Atom': relationship(Atom,
                             primaryjoin=Atom.atom_id==credo.tables['credo.atom_ring_interactions'].c.atom_id,
                             foreign_keys = [Atom.atom_id], uselist=False, innerjoin=True),
        'AromaticRing': relationship(AromaticRing,
                                     primaryjoin=AromaticRing.aromatic_ring_id==credo.tables['credo.atom_ring_interactions'].c.aromatic_ring_id,
                                     foreign_keys = [AromaticRing.aromatic_ring_id], uselist=False, innerjoin=True)
        }
       )

mapper(RingInteraction, credo.tables['credo.ring_interactions'],
       properties = {
        'AromaticRingBgn': relationship(AromaticRing,
                                        primaryjoin=AromaticRing.aromatic_ring_id==credo.tables['credo.ring_interactions'].c.aromatic_ring_bgn_id,
                                        foreign_keys=[AromaticRing.aromatic_ring_id], uselist=False, innerjoin=True),
        'AromaticRingEnd': relationship(AromaticRing,
                                        primaryjoin=AromaticRing.aromatic_ring_id==credo.tables['credo.ring_interactions'].c.aromatic_ring_end_id,
                                        foreign_keys=[AromaticRing.aromatic_ring_id], uselist=False, innerjoin=True),
        'ClosestAtomBgn': relationship(Atom,
                                       primaryjoin=Atom.atom_id==credo.tables['credo.ring_interactions'].c.atom_bgn_id,
                                       foreign_keys = [Atom.atom_id], uselist=False, innerjoin=True),
        'ClosestAtomEnd': relationship(Atom,
                                       primaryjoin=Atom.atom_id==credo.tables['credo.ring_interactions'].c.atom_end_id,
                                       foreign_keys = [Atom.atom_id], uselist=False, innerjoin=True),
        }
       )

mapper(Residue, credo.tables['credo.residues'],
       properties={
        'Atoms': relationship(Atom,
                              primaryjoin=Atom.residue_id==credo.tables['credo.residues'].c.residue_id,
                              foreign_keys = [Atom.residue_id], uselist=True, innerjoin=True,
                              collection_class=column_mapped_collection((Atom.atom_name, Atom.alt_loc)),
                              backref=backref('Residue', uselist=False, innerjoin=True)),
        'AromaticRings': relationship(AromaticRing,
                                      primaryjoin=AromaticRing.residue_id==credo.tables['credo.residues'].c.residue_id,
                                      foreign_keys = [AromaticRing.residue_id], uselist=True, innerjoin=True,
                                      backref=backref('Residue', uselist=False, innerjoin=True)),
       })

mapper(Peptide, credo.tables['credo.peptides'],
       properties={
        'Residue': relationship(Residue,
                                primaryjoin=Residue.residue_id==credo.tables['credo.peptides'].c.residue_id,
                                foreign_keys=[Residue.residue_id], uselist=False, innerjoin=True,
                                backref=backref('Peptide', uselist=False, innerjoin=True)),
        'Atoms': relationship(Atom,
                              collection_class=column_mapped_collection(Atom.atom_name),
                              primaryjoin=Atom.residue_id==credo.tables['credo.peptides'].c.residue_id,
                              foreign_keys = [Atom.residue_id], uselist=True, innerjoin=True),
        'ResMap': relationship(ResMap,
                               primaryjoin=ResMap.res_map_id==credo.tables['credo.peptides'].c.res_map_id,
                               foreign_keys = [ResMap.res_map_id], uselist=False, innerjoin=True),
        'ProtFragment': relationship(ProtFragment,
                                     secondary = credo.tables['credo.prot_fragment_residues'],
                                     primaryjoin=credo.tables['credo.peptides'].c.residue_id==credo.tables['credo.prot_fragment_residues'].c.residue_id,
                                     secondaryjoin=credo.tables['credo.prot_fragment_residues'].c.prot_fragment_id==credo.tables['credo.prot_fragments'].c.prot_fragment_id,
                                     foreign_keys = [credo.tables['credo.prot_fragment_residues'].c.residue_id,
                                                     credo.tables['credo.prot_fragment_residues'].c.prot_fragment_id], uselist=False, innerjoin=True,
                                     backref = backref('Peptides', uselist=True, innerjoin=True)
                                     )
        })

mapper(Nucleotide, credo.tables['credo.nucleotides'],
       properties={
        'Residue': relationship(Residue,
                                primaryjoin=Residue.residue_id==credo.tables['credo.nucleotides'].c.residue_id,
                                foreign_keys=[Residue.residue_id], uselist=False, innerjoin=True,
                                backref=backref('Nucleotide', uselist=False, innerjoin=True)),
        })

mapper(LigandComponent, credo.tables['credo.ligand_components'],
       properties={
        'Atoms': relationship(Atom,
                              collection_class=column_mapped_collection(Atom.atom_name),
                              primaryjoin = Atom.residue_id==credo.tables['credo.ligand_components'].c.residue_id,
                              foreign_keys = [Atom.residue_id], innerjoin=True, uselist=True),
        'Residue': relationship(Residue,
                                primaryjoin=Residue.residue_id==credo.tables['credo.ligand_components'].c.residue_id,
                                foreign_keys=[Residue.residue_id], uselist=False, innerjoin=True),
        'ChemComp': relationship(ChemComp,
                                 primaryjoin=ChemComp.het_id==credo.tables['credo.ligand_components'].c.het_id,
                                 foreign_keys = [ChemComp.het_id], uselist=False, innerjoin=True,
                                 backref=backref('LigandComponents', uselist=True, innerjoin=True)),
        'LigandFragments': relationship(LigandFragment,
                                        primaryjoin=LigandFragment.ligand_component_id==credo.tables['credo.ligand_components'].c.ligand_component_id,
                                        foreign_keys = [LigandFragment.ligand_component_id], uselist=True, innerjoin=True,
                                        backref=backref('LigandComponent', uselist=False, innerjoin=True))
        }
       )

mapper(LigandUSR, credo.tables['credo.ligand_usr'])

mapper(Ligand, credo.tables['credo.ligands'],
       properties={
        'Components': relationship(LigandComponent,
                                      primaryjoin=LigandComponent.ligand_id==credo.tables['credo.ligands'].c.ligand_id,
                                      foreign_keys=[LigandComponent.ligand_id], uselist=True, innerjoin=True,
                                      backref=backref('Ligand', uselist=False, innerjoin=True)),
        'LigandFragments': relationship(LigandFragment,
                                        primaryjoin=LigandFragment.ligand_id==credo.tables['credo.ligands'].c.ligand_id,
                                        foreign_keys = [LigandFragment.ligand_id], uselist=True, innerjoin=True,
                                        backref=backref('Ligand', uselist=False, innerjoin=True)),
        'XRefs': relationship(XRef,
                              primaryjoin=and_(XRef.entity_type=='Ligand', XRef.entity_id==credo.tables['credo.ligands'].c.ligand_id),
                              foreign_keys=[XRef.entity_type, XRef.entity_id], uselist=True, innerjoin=True),
        'name': credo.tables['credo.ligands'].c.ligand_name
        })

mapper(Chain, credo.tables['credo.chains'],
       properties={
        'Residues': relationship(Residue,
                                 collection_class=column_mapped_collection((Residue.res_num, Residue.ins_code)),
                                 primaryjoin=Residue.chain_id==credo.tables['credo.chains'].c.chain_id,
                                 foreign_keys=[Residue.chain_id], uselist=True, innerjoin=True,
                                 backref=backref('Chain', uselist=False, innerjoin=True)),
        'ProtFragments': relationship(ProtFragment,
                                      primaryjoin=ProtFragment.chain_id==credo.tables['credo.chains'].c.chain_id,
                                      foreign_keys=[ProtFragment.chain_id], uselist=True, innerjoin=True,
                                      backref=backref('Chain', uselist=False, innerjoin=True)),
        'XRefs': relationship(XRef,
                              primaryjoin=and_(XRef.entity_type=='Chain', XRef.entity_id==credo.tables['credo.chains'].c.chain_id),
                              foreign_keys=[XRef.entity_type, XRef.entity_id], uselist=True, innerjoin=True),
        'seq': deferred(credo.tables['credo.chains'].c.chain_seq),
        'title': deferred(credo.tables['credo.chains'].c.title)
       }
       )

mapper(Interface, credo.tables['credo.interfaces'],
       properties={
        'ChainBgn': relationship(Chain,
                                 primaryjoin=Chain.chain_id==credo.tables['credo.interfaces'].c.chain_bgn_id,
                                 foreign_keys=[Chain.chain_id], uselist=False, innerjoin=True),
        'ChainEnd': relationship(Chain,
                                 primaryjoin=Chain.chain_id==credo.tables['credo.interfaces'].c.chain_end_id,
                                 foreign_keys=[Chain.chain_id], uselist=False, innerjoin=True),
       }
       )

mapper(Biomolecule, credo.tables['credo.biomolecules'],
       properties={
        'Chains': relationship(Chain,
                               collection_class=column_mapped_collection(Chain.pdb_chain_id),
                               primaryjoin=Chain.biomolecule_id==credo.tables['credo.biomolecules'].c.biomolecule_id,
                               foreign_keys=[Chain.biomolecule_id], uselist=True, innerjoin=True,
                               backref=backref('Biomolecule', uselist=False, innerjoin=True)),
        'Interfaces': relationship(Interface,
                                   primaryjoin=Interface.biomolecule_id==credo.tables['credo.biomolecules'].c.biomolecule_id,
                                   foreign_keys=[Interface.biomolecule_id], uselist=True, innerjoin=True,
                                   backref=backref('Biomolecule', uselist=False, innerjoin=True)),
        'Ligands': relationship(Ligand,
                                primaryjoin=Ligand.biomolecule_id==credo.tables['credo.biomolecules'].c.biomolecule_id,
                                foreign_keys=[Ligand.biomolecule_id], uselist=True, innerjoin=True,
                                backref=backref('Biomolecule', uselist=False, innerjoin=True)),
        'AromaticRings': relationship(AromaticRing,
                                      primaryjoin=AromaticRing.biomolecule_id==credo.tables['credo.biomolecules'].c.biomolecule_id,
                                      foreign_keys=[AromaticRing.biomolecule_id], uselist=True, innerjoin=True,
                                      backref=backref('Biomolecule', uselist=False, innerjoin=True)),
        'Atoms': relationship(Atom,
                              primaryjoin=Atom.biomolecule_id==credo.tables['credo.biomolecules'].c.biomolecule_id,
                              foreign_keys=[Atom.biomolecule_id], uselist=True, innerjoin=True,
                              backref=backref('Biomolecule', uselist=False, innerjoin=True)),
       }
       )

mapper(Structure, credo.tables['credo.structures'],
       properties={
        'Biomolecules': relationship(Biomolecule,
                                     collection_class=column_mapped_collection(Biomolecule.biomolecule),
                                     primaryjoin=Biomolecule.structure_id==credo.tables['credo.structures'].c.structure_id,
                                     foreign_keys=[Biomolecule.structure_id], uselist=True, innerjoin=True,
                                     backref=backref('Structure', uselist=False, innerjoin=True)),
        'XRefs': relationship(XRef,
                              primaryjoin=and_(XRef.entity_type=='Structure', XRef.entity_id==credo.tables['credo.structures'].c.structure_id),
                              foreign_keys=[XRef.entity_type, XRef.entity_id], uselist=True, innerjoin=True),
        'title': deferred(credo.tables['credo.structures'].c.title),
        'authors': deferred(credo.tables['credo.structures'].c.authors)
       }
       )