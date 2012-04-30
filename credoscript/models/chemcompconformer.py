from sqlalchemy.ext.hybrid import hybrid_method

from credoscript import Base

class ChemCompConformer(Base):
    '''
    '''
    __tablename__ = 'pdbchem.chem_comp_conformers'
    
    def __repr__(self):
        '''
        '''
        return '<ChemCompConformer({self.het_id} {self.conformer})>'.format(self=self)

    @classmethod
    def contained_in(self, cube):
        '''
        Returns a PostgreSQL cube database 'contained in' (<@) query as SQLAlchemy
        binary expression.

        Returns
        -------
        expression : sqlalchemy.sql.expression._BinaryExpression

        '''
        return self.usr_space.op('<@')(cube)
        
    def usrcat(self, *expressions, **kwargs):
        '''
        '''
        return ChemCompAdaptor().fetch_all_by_usr_moments(*expressions, usr_space=self.usr_space, usr_moments=self.usr_moments, **kwargs)

from ..adaptors.chemcompadaptor import ChemCompAdaptor