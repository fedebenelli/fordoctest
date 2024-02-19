from fordoctest import FordDocumentationTester, DocumentationError

from unittest.mock import patch

import pytest


@patch('sys.argv', ['', 'test/case1/doc/doc.md'])
def test_undocumented():
    with pytest.raises(DocumentationError):
        tester = FordDocumentationTester()
        tester.analyze()


@patch('sys.argv', ['', 'test/fully_documented/doc.md'])
def test_documented():
    tester = FordDocumentationTester()
    tester.analyze()