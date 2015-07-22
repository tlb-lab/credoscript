"""
This modules contains mapped classes for entities that deal with the CREDO
database itself.
"""
from credoscript import Base, schema

class Update(Base):
    """
    This class is used to represent an update in the CREDO database.
    """
    __tablename__ = '%s.updates' % schema['credo']

    def __repr__(self):
        """
        """
        return "<Update({self.update_id}: {self.update_date})>".format(self=self)