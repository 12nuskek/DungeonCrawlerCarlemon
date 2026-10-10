"""Offline regression: repeated final resource assertion must remain intact."""
from pathlib import Path
import importlib.util
import unittest

spec=importlib.util.spec_from_file_location('corrected',Path(__file__).parent/'test-f1-ordinary-setup-corrected.py')
runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
CODE='if (!strncmp(line,"item ",5)) { int is_item=!strncmp(line,"item ",5); check(); }\nif (!strncmp(line,"uses ",5)) { check(); }'
ROUTE='step 40 0 -\nitem 13 1\nuses 3 40 0 37\nreturn-field\nready\nstep 68 64 -\nitem 13 1\nquit\n'


class Relocation(unittest.TestCase):
    def test_duplicate_final_assertion_retained(self):
        result,proof=runner.corrected_route(ROUTE,CODE)
        self.assertEqual(result,'step 40 0 -\nreturn-field\nready\nitem 13 1\nuses 3 40 0 37\nstep 68 64 -\nitem 13 1\nquit\n')
        self.assertTrue(proof['identical_frame_and_input_commands'])
    def test_wrong_payload_rejected(self):
        with self.assertRaises(AssertionError):runner.corrected_route(ROUTE.replace('uses 3 40 0 37','uses 4 40 0 37'),CODE)
    def test_multiple_windows_rejected(self):
        with self.assertRaises(AssertionError):runner.corrected_route(ROUTE+ROUTE,CODE)
    def test_advancing_handler_rejected(self):
        with self.assertRaises(AssertionError):runner.corrected_route(ROUTE,CODE.replace('check();','core->runFrame(core);'))


if __name__=='__main__':unittest.main()
