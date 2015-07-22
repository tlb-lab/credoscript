from credoscript import Base, schema

class ResMap(Base):
    '''
    Reflects a residue in a sequence-to-structure mapping (PDB-UNIPROT-SCOP).

    Attributes
    ----------
    res_map_id : int
        Primary key of this object.
    ref : string(4)
        Name of the MSD SIFTS reference.
    res_num : int
        MSD SIFTS residue number.
    res_name : string(3)
        MSD SIFTS residue name.
    pdb : string(4)
        PDB code.
    pdb_chain_id : str

    pdb_res_num : int

    pdb_ins_code : str

    pdb_res_name : str

    uniprot : str
        UniProt accession for this mapped residue.
    uniprot_res_num : int
        UniProt residue number for this mapped residue in the UniProt coordinate
        system.
    uniprot_res_name : str
        UniProt one-letter residue name.
    px : int
        SCOP px identifier of this mapped residue.
    scop_chain_id : str

    scop_res_num : int

    scop_ins_code : str

    scop_res_name : str

    Mapped Attributes
    -----------------
    Residue : Residue
        CREDO Residue that is associated with this sequence-to-structure entity.

    References
    ----------
    MSD SIFTS sequence-to-structure mapping
        http://www.ebi.ac.uk/pdbe/docs/sifts/methodology.html
    '''
    __tablename__ = '%s.res_map' % schema['pdb']
    
    def __repr__(self):
        '''
        '''
        return '<ResMap({self.entry} {self.entity_id} {self.db_res_num})>'.format(self=self)