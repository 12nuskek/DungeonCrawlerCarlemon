"""Focused offline regression cases for the diagnosed archive verifier."""
from pathlib import Path
import importlib.util
import unittest

spec=importlib.util.spec_from_file_location('archive_source',Path(__file__).parent/'floor1/ordinary-recovery-source.py')
source=importlib.util.module_from_spec(spec);spec.loader.exec_module(source)


class ArchiveSource(unittest.TestCase):
    def setUp(self):
        self.expected={'marked.pal':(b'A\nB\n',{'text':'set','eol':'crlf'}),
                       'plain.c':(b'C\n',{'text':'set','eol':'lf'}),
                       'unmarked':(b'D\n',{})}
        self.actual={'marked.pal':b'A\r\nB\r\n','plain.c':b'C\n','unmarked':b'D\n'}
    def test_exact_pinned_CRLF_transformation(self):
        source.verify_inventory(self.expected,self.actual)
    def test_content_corruption(self):
        self.actual['marked.pal']=b'A\r\nX\r\n'
        with self.assertRaises(AssertionError):source.verify_inventory(self.expected,self.actual)
    def test_unmarked_EOL_change(self):
        self.actual['unmarked']=b'D\r\n'
        with self.assertRaises(AssertionError):source.verify_inventory(self.expected,self.actual)
    def test_missing_marked_transformation(self):
        self.actual['marked.pal']=b'A\nB\n'
        with self.assertRaises(AssertionError):source.verify_inventory(self.expected,self.actual)
    def test_attribute_change(self):
        self.expected['marked.pal']=(b'A\nB\n',{'text':'set','eol':'lf'})
        with self.assertRaises(AssertionError):source.verify_inventory(self.expected,self.actual)
    def test_pinned_attribute_file_change(self):
        self.expected['.gitattributes']=(b'*.pal text eol=crlf\n',{'text':'set','eol':'lf'})
        self.actual['.gitattributes']=b'*.pal text eol=lf\n'
        with self.assertRaises(AssertionError):source.verify_inventory(self.expected,self.actual)
    def test_missing_tracked_file(self):
        del self.actual['plain.c']
        with self.assertRaises(AssertionError):source.verify_inventory(self.expected,self.actual)
    def test_extra_tracked_file(self):
        self.actual['extra.c']=b'X\n'
        with self.assertRaises(AssertionError):source.verify_inventory(self.expected,self.actual)
    def test_unsupported_attribute(self):
        self.expected['marked.pal']=(b'A\nB\n',{'text':'auto','eol':'crlf'})
        with self.assertRaises(AssertionError):source.verify_inventory(self.expected,self.actual)


if __name__=='__main__':unittest.main()
