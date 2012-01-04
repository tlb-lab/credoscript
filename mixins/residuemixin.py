from sqlalchemy.orm import backref, relationship
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.declarative import declared_attr

class ResidueMixin(object):
    '''
    This Mixin is used for the Residue entity and its children Peptide, Nucleotide,
    Saccharide.
    '''
    def __repr__(self):
        '''
        '''
        return "<{self.__class__.__name__}({self.res_name} {self.res_num}{self.ins_code})>".format(self=self)
    
    def __iter__(self):
        '''
        '''
        return iter(self.Atoms.values())
     
    def __getitem__(self, atom):
        '''
        '''
        # ONLY ATOM NAME IS PROVIDED / WILL TREAT ALTERNATE LOCATION AS BLANK
        if isinstance(atom, str): return self.Atoms.get((atom, ' '))

        # ALTERNATE LOCATION WAS PROVIDED AS WELL
        elif isinstance(atom, tuple): return self.Atoms.get(atom)
    
    @property
    def _res_num_ins_code_tuple(self):
            '''
            Full name of a PDB residue consisting of its residue number and insertion
            code. Only used for the Chain.Residues|Peptides mappers.
            '''
            return self.res_num, str(self.ins_code)   
    
    @property
    def pymolstring(self):
            '''
            Returns a PyMOL selection string in the form /PDB//PDB-CHAIN-ID/RESNAME`RESNUMINSCODE.
            Used by the CREDO PyMOL API.
    
            Returns
            -------
            select : string
                PyMOL selection string.
            '''
            return "/{0}-{1}//{2}/{3}`{4}".format(self.Chain.Biomolecule.Structure.pdb,
                                                  self.Chain.Biomolecule.assembly_serial,
                                                  self.Chain.pdb_chain_id, self.res_name,
                                                  str(self.res_num)+self.ins_code.strip())     
    
    @declared_attr
    def Atoms(self):
        '''
        Returns the atoms of the residue as dictionary collection to allow shortcuts.
        '''
        return relationship("Atom",
                            collection_class=attribute_mapped_collection("full_name"),
                            primaryjoin="and_(Atom.residue_id=={cls}.residue_id, Atom.biomolecule_id=={cls}.biomolecule_id)".format(cls=self.__name__),
                            foreign_keys = "[Atom.residue_id, Atom.biomolecule_id]",
                            uselist=True, innerjoin=True,
                            backref=backref('{cls}'.format(cls=self.__name__),
                                            uselist=False, innerjoin=True))
    
    @declared_attr
    def AromaticRings(self):
        '''
        Returns the aromatic rings of this residue.
        '''
        return relationship("AromaticRing",
                            primaryjoin="AromaticRing.residue_id=={cls}.residue_id".format(cls=self.__name__),
                            foreign_keys = "[AromaticRing.residue_id]",
                            uselist=True, innerjoin=True,
                            backref=backref('{cls}'.format(cls=self.__name__),
                                            uselist=False, innerjoin=True))

class ResidueAdaptorMixin(object):
    '''
    Implements methods to fetch CREDO residues and its inherited entities (peptides,
    nucleotides, saccharides).
    '''  
    def fetch_by_residue_id(self, residue_id):
        '''
        Parameters
        ----------
        residue_id : int
            Primary key of the `Residue` in CREDO.

        Returns
        -------
        Residue
            Residue having the given residue_id as primary key.

        Examples
        --------
        >>> ResidueAdaptor().fetch_by_residue_id(1)
        <Residue(1)>
        '''
        return self.query.get(residue_id)

    def fetch_all_by_chain_id(self, chain_id, *expressions):
        '''
        Returns all residues that are part of the chain with the specified chain_id.
        
        Parameters
        ----------
        chain_id : int
            CREDO chain_id.
        *expressions : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Returns
        -------
        residues : list
            residues that are part of the chain with the specified chain_id.

        Examples
        --------

        '''
        query = self.query.filter("chain_id = :chain_id").params(chain_id=chain_id)
        query = query.filter(and_(*expressions))
        
        return query.all()
    
    def fetch_all_by_biomolecule_id(self, biomolecule_id, *expressions):
        '''
        Returns all residues that are part of the biomolecule with the given
        biomolecule_id.

        Parameters
        ----------
        biomolecule_id : int
            `Biomolecule` identifier.
        *expressions : BinaryExpressions, optional
            SQLAlchemy BinaryExpressions that will be used to filter the query.

        Queried Entities
        ----------------
        Residue

        Returns
        -------
        residues : list
            all residues that are part of the biomolecule with the given biomolecule_id.

         Examples
        --------
        >>> ResidueAdaptor().fetch_all_by_biomolecule_id(4343)

        '''
        query = self.query.filter("biomolecule_id = :biomolecule_id").params(biomolecule_id=biomolecule_id)
        query = query.filter(and_(*expressions))
        
        return query.all()
        