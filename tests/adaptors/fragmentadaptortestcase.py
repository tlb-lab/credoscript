from credoscript import adaptors, models
from tests import CredoAdaptorTestCase

class FragmentAdaptorTestCase(CredoAdaptorTestCase):
    def setUp(self):
        self.adaptor = adaptors.FragmentAdaptor()
        self.expected_entity = models.Fragment

    def test_fetch_by_fragment_id(self):
        """Fetch a single Fragment by fragment_id"""
        self.assertSingleResult('fetch_by_fragment_id', 1)

    def test_fetch_all_by_het_id(self):
        """Fetch Fragments by het_id"""
        self.assertPaginatedResult('fetch_all_by_het_id', 'STI')

    def test_fetch_all_children(self):
        """Fetch all child fragments of a Fragment by fragment_id"""
        fragment = self.adaptor.fetch_all_by_het_id('STI')[-1]
        self.assertPaginatedResult('fetch_all_children', fragment.fragment_id)

    def test_fetch_all_parents(self):
        """Fetch all parent fragments of a Fragment by fragment_id"""
        fragment = self.adaptor.fetch_all_by_het_id('STI')[5]
        self.assertPaginatedResult('fetch_all_parents', fragment.fragment_id)

    def test_fetch_all_descendants(self):
        """Fetch all descendants of a Fragment by fragment_id"""
        fragment = self.adaptor.fetch_all_by_het_id('STI')[5]
        self.assertPaginatedResult('fetch_all_descendants', fragment.fragment_id)

    def test_fetch_all_leaves(self):
        """Fetch all leave children of a Fragment by fragment_id"""
        fragment = self.adaptor.fetch_all_by_het_id('STI')[-1]
        self.assertPaginatedResult('fetch_all_leaves', fragment.fragment_id)