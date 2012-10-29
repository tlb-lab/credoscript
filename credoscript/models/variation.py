from sqlalchemy.orm import backref, relationship

from credoscript import Base

class Source(Base):
    """
    """
    __tablename__ = 'variations.sources'

class TranscriptVariation(Base):
    """
    """
    __tablename__ = 'variations.transcript_variations'

class Variation(Base):
    """
    """
    __tablename__ = 'variations.variations'

    Source = relationship("Source",
                          primaryjoin="Variation.source_id==Source.source_id",
                          foreign_keys="[Source.source_id]",
                          uselist=False, innerjoin=True)

    Annotations = relationship("Annotation",
                               primaryjoin="Variation.variation_id==Annotation.variation_id",
                               foreign_keys="[Annotation.variation_id]",
                               uselist=True, innerjoin=True,
                               backref=backref('Variation', uselist=False))

    Variation2UniProt = relationship("Variation2UniProt",
                                     primaryjoin="Variation.variation_id==Variation2UniProt.variation_id",
                                     foreign_keys="[Variation2UniProt.variation_id]",
                                     uselist=True, innerjoin=True,
                                     backref=backref('Variation', uselist=False))

    Variation2PDB = relationship("Variation2PDB",
                       secondary = Base.metadata.tables['variations.variation_to_uniprot'],
                       primaryjoin = "Variation.variation_id==Variation2UniProt.variation_id",
                       secondaryjoin = "Variation2UniProt.variation_to_uniprot_id==Variation2PDB.variation_to_uniprot_id",
                       foreign_keys = "[Variation2UniProt.variation_id, Variation2PDB.variation_to_uniprot_id]",
                       uselist=True, innerjoin=True,
                       backref=backref('Variation', uselist=False, innerjoin=True))

    TranscriptVariations = relationship("TranscriptVariation",
                                        primaryjoin="Variation.variation_id==TranscriptVariation.variation_id",
                                        foreign_keys="[TranscriptVariation.variation_id]",
                                        uselist=True, innerjoin=True,
                                        backref=backref('Variation', uselist=False))

    def __repr__(self):
        """
        """
        return '<Variation({self.variation_name})>'.format(self=self)

class Variation2UniProt(Base):
    """
    """
    __tablename__ = 'variations.variation_to_uniprot'

    Variation2PDB = relationship("Variation2PDB",
                                 primaryjoin = "Variation2UniProt.variation_to_uniprot_id==Variation2PDB.variation_to_uniprot_id",
                                 foreign_keys = "[Variation2PDB.variation_to_uniprot_id]",
                                 uselist=True, innerjoin=True,
                                 backref=backref('Variation2UniProt', uselist=False, innerjoin=True))

    def __repr__(self):
        """
        """
        return '<Variation2UniProt({self.uniprot}: {self.wt}{self.uniprot_res_num_start}{self.mut})>'.format(self=self)

class Variation2PDB(Base):
    """
    """
    __tablename__ = 'variations.variation_to_pdb'

    Peptide = relationship("Peptide",
                           primaryjoin="Variation2PDB.res_map_id==Peptide.res_map_id",
                           foreign_keys="[Peptide.res_map_id]",
                           uselist=False, innerjoin=True,
                           backref=backref('Variation2PDB', uselist=False))

class Annotation(Base):
    """
    """
    __tablename__ = 'variations.annotations'

    Phenotype = relationship("Phenotype",
                             primaryjoin="Annotation.phenotype_id==Phenotype.phenotype_id",
                             foreign_keys="[Phenotype.phenotype_id]",
                             uselist=False, innerjoin=True,
                             backref=backref('Annotations', uselist=True))

    def __repr__(self):
        """
        """
        return '<Annotation({self.variation_annotation_id})>'.format(self=self)

class Phenotype(Base):
    """
    """
    __tablename__ = 'variations.phenotypes'

    def __repr__(self):
        """
        """
        return '<Phenotype({self.phenotype_id})>'.format(self=self)