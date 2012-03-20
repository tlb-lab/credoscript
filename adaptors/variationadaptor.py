from credoscript import metadata

variation_to_pdb = metadata.tables.get('variations.variation_to_pdb')
variation_to_uniprot = metadata.tables.get('variations.variation_to_uniprot')

class VariationAdaptor(object):
    """
    """
    def fetch_by_variation_id(self, variation_id):
        """
        """
        return Variation.query.get(variation_id)
        
    def fetch_all_by_res_map_id(self, res_map_id):
        """
        """
        query = Variation.query
        query = query.join(variation_to_uniprot, variation_to_uniprot.c.variation_id==Variation.variation_id)
        query = query.join(variation_to_pdb, variation_to_pdb.c.variation_to_uniprot_id==variation_to_uniprot.c.variation_to_uniprot_id)
        query = query.filter(variation_to_pdb.c.res_map_id==res_map_id)
        
        return query

from ..models.variation import Variation