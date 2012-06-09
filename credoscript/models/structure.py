from sqlalchemy import Integer, select
from sqlalchemy.sql.expression import and_, cast
from sqlalchemy.orm import backref, deferred, relationship
from sqlalchemy.orm.collections import attribute_mapped_collection

from credoscript import Base, Session, citations

class Structure(Base):
    """
    Represents a PDB Structure entity from CREDO.

    Attributes
    ----------
    structure_id : int
        Primary key.
    pdb : string
        PDB 4-letter code.
    title : string
        A title for the data block. The author should attempt to convey the
        essence of the structure archived in the CIF in the title, and to
        distinguish this structural result from others (struct.title).
    authors : string
        Concatenated string of author names.
    exptl : string
        The method used in the experiment (exptl.method).
    deposition :
        Date the entry first entered the PDB database in the form  yyyy-mm-dd.
        Taken from the PDB HEADER record (database_PDB_rev.date_original).
    release :
        Date the PDB revision took place. Taken from the REVDAT record
        (database_PDB_rev.date).
    resolution : float
        The smallest value for the interplanar spacings for the reflection data
        used in the refinement in angstroms. This is called the highest
        resolution (refine.ls_d_res_high).
    r_factor : float
        Residual factor R for reflections* that satisfy the
        reflns.observed_criterion were included in the refinement (when the
        refinement included the calculation of a 'free' R factor)
        (refine.ls_R_factor_R_work).
    r_free : float
        Residual factor R for reflections that satisfy the
        reflns.observed_criterion that were used as test reflections (i.e. were
        excluded from the refinement) (refine.ls_R_factor_R_free)
    pH : float
        The pH at which the crystal was grown (exptl_crystal_grow.pH).
    dpi: float
        Diffraction-Component Precision Index.
    dpi_theoretical_min: float
        The theoretical minimal value of the DPI.
    num_biomolecules : int
        Number of biomolecules generated for this Structure.

    Mapped Attributes
    -----------------
    biomolecules : Query
        All biomolecules that have this `Structure` as parent. '0' means that a
        stable prediction was not found in PISA.
    biomolecule_map : dict
        Dictionary in the form {biomolecule: Biomolecule} containing all biomolecules
        that have this `Structure` as parent. '0' means that a stable prediction
        was not found in PISA.
    xrefs : Query
        CREDO XRef objects that are associated with this Structure Entity.
    abstracts:


    See Also
    --------
    StructureAdaptor : Fetch Structures from the database.

    Notes
    -----
    - The __getitem__ method is overloaded so that Structure[1] will return
      the first Biomolecule (biological assembly) of this structure
    """
    __table__ = Base.metadata.tables['credo.structures']

    Biomolecules = relationship("Biomolecule",
                                primaryjoin="Biomolecule.structure_id==Structure.structure_id",
                                foreign_keys="[Biomolecule.structure_id]",
                                uselist=True, innerjoin=True, lazy='dynamic',
                                backref=backref('Structure', uselist=False, innerjoin=True))

    # map biomolecules as dictionary in the form {<assembly serial>: biomolecule}
    BiomoleculeMap = relationship("Biomolecule",
                                   collection_class=attribute_mapped_collection("assembly_serial"),
                                   primaryjoin="Biomolecule.structure_id==Structure.structure_id",
                                   foreign_keys="[Biomolecule.structure_id]",
                                   uselist=True, innerjoin=True)

    XRefs = relationship("XRef",
                         primaryjoin="and_(XRef.entity_type=='Structure', XRef.entity_id==Structure.structure_id)",
                         foreign_keys="[XRef.entity_type, XRef.entity_id]",
                         uselist=True, innerjoin=True, lazy='dynamic')

    # deferred columns
    title = deferred(__table__.c.title)
    authors = deferred(__table__.c.authors)

    def __repr__(self):
        """
        """
        return "<Structure({self.pdb})>".format(self=self)

    def __getitem__(self, assembly_serial):
        """
        Returns the Biomolecule with the specified biomolecule serial number or
        None.

        Parameters
        ----------
        assembly_serial : int
            Serial number of the biological assembly derived from this Structure.

        Returns
        -------
        biomolecule : Biomolecule

        """
        return self.BiomoleculeMap.get(assembly_serial)

    def __iter__(self):
        """
        Returns the Biomolecules of this Structure.

        Returns
        -------
        biomolecules : list
            Biological assemblies derived from this asymmetric unit.
        """
        return iter(self.Biomolecules.all())

    @property
    def abstracts(self):
        """
        Returns the abstract(s) of the journal articles that are associated with
        this PDB entry.
        """
        session = Session()

        statement = select([citations],
            and_(citations.c.pubmed_id==cast(XRef.xref, Integer),
                 XRef.source=='PubMed', XRef.entity_type=='Structure',
                 XRef.entity_id==self.structure_id))

        return session.execute(statement).fetchall()

from ..models.xref import XRef
