import unittest
import edmv
import sys
import io

def run_trial(sources, destinations, retries=0):
    def test_editor(filename):
        with open(filename, 'w') as f:
            f.write("\n".join(destinations))

    def strip_uuid(s):
        if s.endswith('.edmv'):
            pos = s.rfind('.', 0, -len('.edmv'))
            s = s[:pos] + '.[UUID].edmv'
        return s

    mv_log = []
    def test_mv(src, dest):
        if 'ERROR' in (src, dest):
            raise Exception("Simulated error")
        else:
            mv_log.append((strip_uuid(src), strip_uuid(dest)))

    stdin = sys.stdin
    stdout = sys.stdout
    stderr = sys.stderr
    try:
        sys.stdin = io.StringIO('y\n' * retries + 'n\n')
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()
        status = edmv.edmv(sources, editor = test_editor, mv = test_mv)
        return mv_log, status, sys.stdout.getvalue(), sys.stderr.getvalue()
    finally:
        sys.stderr = stderr
        sys.stdout = stdout
        sys.stdin = stdin

class TrialTestRaw():
    retries = 0

    def setUp(self):
        result = run_trial(self.sources, self.destinations, self.retries)
        self.mv_log, self.status, self.stdout, self.stderr = result

    def testMoves(self):
        self.assertListEqual(self.mv_log, list(self.expected_moves))

    def testStatus(self):
        if 'expected_status' in dir(self):
            self.assertEqual(self.status, self.expected_status)
        else:
            self.assertEqual(self.status, True)

    def testStdout(self):
        if 'expected_stdout' in dir(self):
            self.assertEqual(self.stdout, self.expected_stdout)
        else:
            self.assertEqual(self.stdout, "")

    def testStderr(self):
        if 'expected_stderr' in dir(self):
            self.assertEqual(self.stderr, self.expected_stderr)
        else:
            self.assertEqual(self.stderr, "")

class TrialTest(TrialTestRaw):
    def setUp(self):
        sources = [x[0] for x in self.moves]
        contents = [x[1] for x in self.moves]
        result = run_trial(sources, contents, self.retries)
        self.mv_log, self.status, self.stdout, self.stderr = result

class TestNormal(TrialTest, unittest.TestCase):
    moves = (
        ('a', 'b'),
        ('c', 'c'),
    )

    expected_moves = (
        ('a', 'b'),
    )

class TestCycling(TrialTest, unittest.TestCase):
    moves = (
        ('a', 'b'),
        ('b', 'a'),
    )

    expected_moves = (
        ('a', 'b.[UUID].edmv'),
        ('b', 'a.[UUID].edmv'),
        ('b.[UUID].edmv', 'b'),
        ('a.[UUID].edmv', 'a'),
    )

class TestMixture(TrialTest, unittest.TestCase):
    moves = (
        ('a', 'b'),
        ('b', 'c'),
        ('c', 'a'),
        ('1', '1'),
        ('2', '3'),
    )

    expected_moves = (
        ('a', 'b.[UUID].edmv'),
        ('b', 'c.[UUID].edmv'),
        ('c', 'a.[UUID].edmv'),
        ('2', '3'),
        ('b.[UUID].edmv', 'b'),
        ('c.[UUID].edmv', 'c'),
        ('a.[UUID].edmv', 'a'),
    )

class TestFailAndUndo(TrialTest, unittest.TestCase):
    moves = (
        ('a', 'b'),
        ('b', 'c'),
        ('c', 'a'),
        ('1', '1'),
        ('2', '3'),
        ('5', 'ERROR'),
        ('6', '7'),
    )

    expected_moves = (
        ('a', 'b.[UUID].edmv'),
        ('b', 'c.[UUID].edmv'),
        ('c', 'a.[UUID].edmv'),
        ('2', '3'),
        ('3', '2'),
        ('a.[UUID].edmv', 'c'),
        ('c.[UUID].edmv', 'b'),
        ('b.[UUID].edmv', 'a'),
    )

    expected_stderr = (
        "Error: Simulated error\n"
        "Undoing...\n"
    )

    expected_status = False

class TestEmptyDestExits(TrialTestRaw, unittest.TestCase):
    sources = (
        'a',
    )

    destinations = (
        '',
    )

    expected_moves = (
    )

    expected_status = False

class TestExtraPath(TrialTestRaw, unittest.TestCase):
    sources = (
        'a',
    )

    destinations = (
        'a',
        'b',
    )

    expected_moves = (
    )

    expected_stdout = (
        "Re-edit? [Y/n] "
    )

    expected_stderr = (
        "Got 2 new paths (expected 1).\n"
    )

    expected_status = False

class TestMissingPath(TrialTestRaw, unittest.TestCase):
    sources = (
        'a',
        'b',
    )

    destinations = (
        'a',
    )

    expected_moves = (
    )

    expected_stdout = (
        "Re-edit? [Y/n] "
    )

    expected_stderr = (
        "Got 1 new paths (expected 2).\n"
    )

    expected_status = False

class TestEmptyPath(TrialTestRaw, unittest.TestCase):
    sources = (
        'a',
        'b',
    )

    destinations = (
        '',
        'c',
    )

    expected_moves = (
    )

    expected_stdout = (
        "Re-edit? [Y/n] "
    )

    expected_stderr = (
            "Cannot rename to empty path:\n"
            "a\n"
    )

    expected_status = False

class TestDuplicatePaths(TrialTestRaw, unittest.TestCase):
    sources = (
        'a',
        'b',
    )

    destinations = (
        'c',
        'c',
    )

    expected_moves = (
    )

    expected_stdout = (
        "Re-edit? [Y/n] "
    )

    expected_stderr = (
        "Paths must all be unique:\n"
        "c\n"
    )

    expected_status = False

if __name__ == '__main__':
    unittest.main()
