"""
This modules contains mapped classes for entities that deal with the CREDO
database itself.
"""
from credoscript import Base

class Update(Base):
    """
    This class is used to represent an update in the CREDO database.
    """
    __tablename__ = 'credo.updates'

    def __repr__(self):
        """
        """
        return "<Update({self.update_id}: {self.update_date})>".format(self=self)