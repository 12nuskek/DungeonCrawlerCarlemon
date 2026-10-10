"""Focused tests for the new dynamic reference's strict grammar/integrity/EOF."""
from pathlib import Path
import importlib.util, struct, tempfile, unittest
spec=importlib.util.spec_from_file_location('new_reference',Path(__file__).parent/'floor1/v01-new-input-reference.py')
parser=importlib.util.module_from_spec(spec);spec.loader.exec_module(parser)
HEADER=struct.Struct('<cQIIIII')
def stream():
    return HEADER.pack(b'B',0,0,2045,0,2044,0)+bytes(2560)+HEADER.pack(b'F',1,0,2045,1,2045,0)+HEADER.pack(b'E',1,0,2045,0,2045,0)
class Reference(unittest.TestCase):
    def check(self,data):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'trace';p.write_bytes(data);return parser.scan(p)
    def test_new_counts_without_historical_pins(self):
        value=self.check(stream());self.assertEqual((value['boundaries'],value['frames']),(1,1));self.assertTrue(value['typed_finish_complete'])
    def test_rejects_truncations(self):
        for n in [1,28,29,2000,len(stream())-1]:
            with self.subTest(n=n),self.assertRaises(AssertionError):self.check(stream()[:n])
    def test_rejects_post_finish(self):
        with self.assertRaises(AssertionError):self.check(stream()+b'x')
    def test_rejects_metadata_changes(self):
        for offset in [1,9,13,17,21,2589+17,2618+25]:
            data=bytearray(stream());data[offset]^=1
            with self.subTest(offset=offset),self.assertRaises(AssertionError):self.check(data)
    def test_rejects_native_party_checksum(self):
        data=bytearray(stream());data[29+32]=1
        with self.assertRaises(AssertionError):self.check(data)
    def test_rejects_bad_egg(self):
        data=bytearray(stream());data[29+19]=1
        with self.assertRaises(AssertionError):self.check(data)
if __name__=='__main__':unittest.main()
