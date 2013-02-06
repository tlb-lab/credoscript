from sqlalchemy.sql.expression import and_

from credoscript.mixins import PathAdaptorMixin, ResidueAdaptorMixin
from credoscript.mixins.base import paginate

class PeptideAdaptor(ResidueAdaptorMixin, PathAdaptorMixin):
    """
    """
    def __init__(self, dynamic=False, paginate=False, per_page=100):
        self.query = Peptide.query
        self.dynamic = dynamic
        self.paginate = paginate
        self.per_page = per_page

    def fetch_by_res_map_id(self, res_map_id):
        """
        """
        return self.query.filter_by(res_map_id=res_map_id).first()

    @paginate
    def fetch_all_by_variation_id(self, variation_id, *expr, **kwargs):
        """
        """
        query = self.query.join('Variation2PDB','Variation2UniProt')
        query = query.filter(and_(Variation2UniProt.variation_id==variation_id,
                                  *expr))

        # add more variation data to the returned entities
        if kwargs.get('vardata'):
            query = query.add_entity(Variation2UniProt)

        return query.distinct()

    @paginate
    def fetch_all_by_phenotype_id(self, phenotype_id, *expr, **kwargs):
        """
        """
        query = self.query.join('Variation2PDB','Variation2UniProt','Variation','Annotations')
        query = query.filter(and_(Annotation.phenotype_id==phenotype_id,
                                  *expr))

        # add more variation data to the returned entities
        if kwargs.get('vardata'):
            query = query.add_entity(Variation2UniProt)

        return query.distinct()

    @paginate
    def fetch_all_having_variations_by_chain_id(self, chain_id, *expr, **kwargs):
        """
        Returns all peptides in a chain that have mapped variations.
        """
        query = self.query.join('Variation2PDB','Variation2UniProt')
        query = query.filter(and_(Peptide.chain_id==chain_id, *expr))

        # add more variation data to the returned entities
        if kwargs.get('vardata'):
            query = query.add_entity(Variation2UniProt)

        return query.distinct()

    @paginate
    def fetch_all_having_variations_by_biomolecule_id(self, biomolecule_id, *expr,
                                                      **kwargs):
        """
        Returns all peptides in a biologcial assembly that have mapped variations.
        """
        query = self.query.join('Variation2PDB','Variation2UniProt')
        query = query.filter(and_(Peptide.biomolecule_id==biomolecule_id, *expr))

        # add more variation data to the returned entities
        if kwargs.get('vardata'):
            query = query.add_entity(Variation2UniProt)

        return query.distinct()

    @paginate
    def fetch_all_having_variations_in_contact_with_ligand_id(self, ligand_id,
                                                              *expr, **kwargs):
        """
        Returns all peptides that have mapped variations and are in contact with
        the ligand having the input ligand identifier.
        """
        query = self.query.join('Variation2PDB','Variation2UniProt')
        query = query.join(BindingSiteResidue, BindingSiteResidue.residue_id==Peptide.residue_id)
        query = query.filter(and_(BindingSiteResidue.ligand_id==ligand_id, *expr))

        # add more variation data to the returned entities
        if kwargs.get('vardata'):
            query = query.add_entity(Variation2UniProt)

        return query.distinct()

from ..models.peptide import Peptide
from ..models.bindingsite import BindingSiteResidue
from ..models.variation import Variation2UniProt, Annotation
