from credoscript import adaptors, models
from tests import CredoAdaptorTestCase

class ChainAdaptorTestCase(CredoAdaptorTestCase):
    def setUp(self):
        self.adaptor = adaptors.ChainAdaptor()
        self.expected_entity = models.Chain

    def test_fetch_by_chain_id(self):
        """Fetch a single chain by chain_id"""
        self.assertSingleResult('fetch_by_chain_id', 1)

    def test_fetch_all_by_structure_id(self):
        """Fetch chains by structure_id"""
        self.assertPaginatedResult('fetch_all_by_structure_id', 1)

    def test_fetch_all_by_domain_id(self):
        """Fetch chains by domain_id"""
        self.assertPaginatedResult('fetch_all_by_domain_id', 1)

    def test_fetch_all_polypeptides(self):
        """Fetch all polypeptides"""
        self.assertPaginatedResult('fetch_all_polypeptides')

    def test_fetch_all_oligonucleotides(self):
        """Fetch all oligonucleotides"""
        self.assertPaginatedResult('fetch_all_oligonucleotides')

    def test_fetch_all_kinases(self):
        """Fetch all kinases"""
        self.assertPaginatedResult('fetch_all_kinases')

    def test_fetch_all_biotherapeutics(self):
        """Fetch all kinases"""
        self.assertPaginatedResult('fetch_all_biotherapeutics')

    def test_fetch_all_by_uniprot(self):
        """Fetch chains by UniProt accession"""
        self.assertPaginatedResult('fetch_all_by_uniprot', 'P00520')

    def test_fetch_all_by_cath_dmn(self):
        """Fetch chains by CATH domain accession"""
        self.assertPaginatedResult('fetch_all_by_cath_dmn', '2p33A00')

    def test_fetch_all_by_seq_md5(self):
        """Fetch chains by CATH domain accession"""
        self.assertPaginatedResult('fetch_all_by_seq_md5',
                                   '02F49E94352EADF3DE9DC9416502ED7F')