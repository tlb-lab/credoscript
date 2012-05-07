from credoscript import adaptors, models
from tests import CredoAdaptorTestCase

class LigandMatchAdaptorTestCase(CredoAdaptorTestCase):
    def setUp(self):
        self.adaptor = adaptors.LigandMatchAdaptor()
        self.expected_entity = models.LigandMatch

    def test_fetch_substruct_matches(self):
        """"""
        matches = self.adaptor.fetch_substruct_matches('c1cc(cnc1)c2ccncn2')

        for match in matches:
            self.assertIsInstance(match, self.expected_entity)

    def test_fetch_smarts_matches(self):
        """"""
        matches = self.adaptor.fetch_smarts_matches('c1cc(cnc1)c2ccncn2')

        for match in matches:
            self.assertIsInstance(match, self.expected_entity)