from sqlalchemy.orm import Query

from credoscript import adaptors, models
from credoscript.mixins import Pagination

from tests import CredoAdaptorTestCase

class StructureAdaptorTestCase(CredoAdaptorTestCase):
    def setUp(self):
        self.adaptor = adaptors.StructureAdaptor()
        self.expected_entity = models.Structure

    def test_fetch_by_structure_id(self):
        """Fetch a single structure by structure_id"""
        self.assertSingleResult('fetch_by_structure_id', 1)

    def test_fetch_by_pdb(self):
        """Fetch a single structure by PDB code"""
        self.assertSingleResult('fetch_by_pdb', '2P33')

    def test_fetch_all_by_het_id(self):
        """Fetch all structures containing ligands matching a HET-ID"""
        self.assertPaginatedResult('fetch_all_by_het_id', 'STI')

    def test_fetch_all_by_uniprot(self):
        """Fetch all structures containing polypeptides chains matching a UniProt accessions"""
        self.assertPaginatedResult('fetch_all_by_uniprot', 'P00520')

    def test_fetch_all_by_tsquery(self):
        """Fetch all structures by abstract text search"""
        # this should return a list of tuples in the form (similarity, entity)
        result = getattr(self.adaptor, 'fetch_all_by_tsquery')('protein-protein interaction inhibitor', plain=True)

        assert all(isinstance(ent, self.expected_entity) for ent, rank in result), "{} does not return the correct result tuple.".format('fetch_all_by_tsquery')

        self.adaptor.dynamic = True
        result = getattr(self.adaptor, 'fetch_all_by_tsquery')('protein-protein interaction inhibitor', plain=True)
        assert isinstance(result, Query), "{} does not support dynamic results.".format('fetch_all_by_tsquery')
        self.adaptor.dynamic = False

        # this should return a Pagination object
        self.adaptor.paginate = True
        result = getattr(self.adaptor, 'fetch_all_by_tsquery')('protein-protein interaction inhibitor', plain=True, page=1)
        assert isinstance(result, Pagination), "{} does not support pagination.".format('fetch_all_by_tsquery')
        self.adaptor.paginate = False