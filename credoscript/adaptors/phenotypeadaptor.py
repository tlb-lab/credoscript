from sqlalchemy.sql.expression import and_, func

from credoscript.mixins.base import paginate

class PhenotypeAdaptor(object):
    """
    CREDO adaptor to fetch EnsEMBL variation phenotypes from the database.
    """
    def __init__(self, dynamic=False, paginate=False, per_page=100):
        self.query = Phenotype.query
        self.dynamic = dynamic
        self.paginate = paginate
        self.per_page = per_page

    def fetch_by_phenotype_id(self, phenotype_id):
        """
        """
        return self.query.get(phenotype_id)

    @paginate
    def fetch_all_by_variation_id(self, variation_id, *expr, **kwargs):
        """
        Return all phenotypes associated with a given variation_id.
        """
        query = self.query.join('Annotations')
        query = query.filter(and_(Annotation.variation_id==variation_id, *expr))
        query = query.distinct()

        return query

    @paginate
    def fetch_all_by_variation_annotation_id(self, variation_annotation_id,
                                             *expr, **kwargs):
        """
        Return all phenotypes associated with a given variation_annotation_id.
        """
        query = self.query.join('Annotations')
        query = query.filter(and_(Annotation.variation_annotation_id==variation_annotation_id,
                                  *expr))
        query = query.distinct()

        return query

    @paginate
    def fetch_all_by_description(self, description, *expr, **kwargs):
        """
        Return all phenotypes whose description matches the given keyword(s).
        """
        return self.query.filter(
            and_(func.lower(Phenotype.description).contains(description),
                 *expr))

from credoscript.models.variation import Phenotype