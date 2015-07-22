import re
from sqlalchemy.orm import backref, relationship

from credoscript import Base, schema
from credoscript.mixins import PathMixin


class ProtFragment(Base, PathMixin):
    '''
    '''
    __tablename__ = '%s.prot_fragments' % schema['credo']

    Peptides = relationship("Peptide",
                            secondary = Base.metadata.tables['%s.prot_fragment_residues' % schema['credo']],
                            primaryjoin = "ProtFragment.prot_fragment_id==ProtFragmentResidue.prot_fragment_id",
                            secondaryjoin = "ProtFragmentResidue.residue_id==Peptide.residue_id",
                            foreign_keys = "[ProtFragmentResidue.prot_fragment_id, Peptide.residue_id]",
                            uselist=True, innerjoin=True, lazy='dynamic',
                            backref = backref('ProtFragment', uselist=False, innerjoin=True))

    def __repr__(self):
        '''
        '''
        return '<ProtFragment({self.path})>'.format(self=self)

    @property
    def ProtFragmentN(self):
        '''
        '''
        return ProtFragmentAdaptor().fetch_by_prot_fragment_id(self.prot_fragment_nterm_id)

    @property
    def ProtFragmentC(self):
        '''
        '''
        return ProtFragmentAdaptor().fetch_by_prot_fragment_id(self.prot_fragment_cterm_id)

    @property
    def IdenticalFragments(self):
        '''
        '''
        adaptor = ProtFragmentAdaptor(dynamic=True)
        return adaptor.fetch_all_by_fragment_seq(self.fragment_seq)

    @property
    def pymolstring(self):
        """
        Returns a PyMOL selection string for this protein secondary structure
        fragment.
        
        Example
        -------
        /2P33//A/64+65+66+67+68+69+70+71+72
        """
        if self.completeness > 0:

            # get the residue number of the peptide that form this fragment
            resnums = sorted(peptide.res_num for peptide in self.Peptides.all())

            # remove the internal terminal path label (PF:X)
            path = self.path.rsplit('/', 1)[0]

            # remove the biomolecule identifier subpath
            path = '/' + re.sub('/\d+/','//', path)

            # append the residue numbers
            return path + '/' + '+'.join(map(str, resnums))

from ..adaptors.protfragmentadaptor import ProtFragmentAdaptor
