from fordoctest import FordDocumentationTester

from unittest.mock import patch


def test_analyize():
    with patch('sys.argv', ['case1/doc/doc.md']):
        import sys
        print(sys.argv)
        tester = FordDocumentationTester()
        print("coso")
        tester.analyze()
