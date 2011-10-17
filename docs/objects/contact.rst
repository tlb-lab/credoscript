********
Contacts
********

Attributes
==========

===========================  =====  ======================================================================================
attribute                    type   description
===========================  =====  ======================================================================================
contact_id                   int    primary key
biomolecule_id               int    primary key of the parent :doc:`biomolecule </objects/biomolecule>`
atom_bgn_id                  int    primary key of the first atom
atom_end_id                  int    primary key of the first atom
distance real                float  interatomic distance in A
structural_interaction_type  int    sum of the entity type bit masks of the interacting :doc:`residues </objects/residue>`
is_same_entity               bool   true if the interacting atoms belong to the same entity
is_secondary                 bool   true if the interaction is classified as secondary
is_covalent                  bool 
is_vdw_clash                 bool
is_vdw                       bool
is_proximal                  bool 
is_hbond                     bool
is_weak_hbond                bool
is_xbond                     bool
is_ionic                     bool
is_metal_complex             bool
is_aromatic                  bool 
is_hydrophobic               bool 
is_carbonyl                  bool
===========================  =====  ======================================================================================

Relationships
=============

Methods
=======