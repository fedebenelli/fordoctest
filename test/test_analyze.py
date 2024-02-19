from fordoctest import FordDocumentationTester, DocumentationWarning

from unittest.mock import patch

import pytest


@patch('sys.argv', ['', 'test/case1/doc/doc.md'])
def test_undocumented():
    with pytest.warns(DocumentationWarning):
        tester = FordDocumentationTester()
        tester.analyze()
