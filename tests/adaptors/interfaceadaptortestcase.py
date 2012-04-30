from credoscript import adaptors, models
from tests import CredoAdaptorTestCase

class InterfaceAdaptorTestCase(CredoAdaptorTestCase):
    def setUp(self):
        self.adaptor = adaptors.InterfaceAdaptor()
        self.expected_entity = models.Interface

    def test_fetch_by_interface_id(self):
        """Fetch a single Interface by interface_id"""
        self.assertSingleResult('fetch_by_interface_id', 1)

    def test_fetch_all_by_chain_id(self):
        """Fetch all interfaces by chain_id"""
        interface = models.Interface.query.get(1)
        self.assertPaginatedResult('fetch_all_by_chain_id',
                                   interface.chain_bgn_id)

    def test_fetch_all_by_biomolecule_id(self):
        """Fetch all interfaces by biomolecule_id"""
        interface = models.Interface.query.get(1)
        self.assertPaginatedResult('fetch_all_by_biomolecule_id',
                                   interface.biomolecule_id)

    def test_fetch_all_by_uniprot(self):
        """Fetch all interfaces by UniProt accession"""
        self.assertPaginatedResult('fetch_all_by_uniprot', 'P09211')

    def test_fetch_all_cath_dmn(self):
        """Fetch all interfaces by UniProt accession"""
        self.assertPaginatedResult('fetch_all_by_cath_dmn', '10gsA01')

    def test_fetch_all_by_phenotype_id(self):
        """Fetch all interfaces by variation phenotype_id"""
        self.assertPaginatedResult('fetch_all_by_phenotype_id', 13)

    def test_fetch_all_by_path_match(self):
        """retrieve interfaces through ptree path match"""
        self.assertPaginatedResult('fetch_all_by_path_match', '11GS/*')

    def test_fetch_all_path_descendants(self):
        """retrieve interfaces through ptree path descendants"""
        self.assertPaginatedResult('fetch_all_path_descendants', '11GS/1')