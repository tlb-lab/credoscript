from credoscript import Base, schema

class ChemCompConformer(Base):
    """
    """
    __tablename__ = '%s.chem_comp_conformers' % schema['pdbchem']

    def __repr__(self):
        """
        """
        return '<ChemCompConformer({self.het_id} {self.conformer})>'.format(self=self)

    @classmethod
    def contained_in(self, cube):
        """
        Returns a PostgreSQL cube database 'contained in' (<@) query as SQLAlchemy
        binary expression.

        Returns
        -------
        expression : sqlalchemy.sql.expression._BinaryExpression

        """
        return self.usr_space.op('<@')(cube)

    def usrcat(self, *expr, **kwargs):
        """
        """
        return ChemCompAdaptor().fetch_all_by_usr_moments(*expr,
                                                          usr_space=self.usr_space,
                                                          usr_moments=self.usr_moments,
                                                          **kwargs)

from ..adaptors.chemcompadaptor import ChemCompAdaptor
