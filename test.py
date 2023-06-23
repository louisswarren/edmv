import unittest
import edmv
import sys
import io

def run_trial(trial, retries=0):
    sources = [x[0] for x in trial]

    contents = "\n".join((x[1] for x in trial))
    def test_editor(filename):
        with open(filename, 'w') as f:
            f.write(contents)

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

class TrialTest():
    def run_trial(self, trial, retries=0):
        result = run_trial(trial, retries)
        self.mv_log, self.status, self.stdout, self.stderr = result

    def setUp(self):
        self.run_trial(self.moves)

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


class TestNormal(TrialTest, unittest.TestCase):
    moves = (
        ('a', 'b'),
        ('c', 'c'),
    )

    expected_moves = (
        ('a', 'b'),
    )

    expected_stdout = ""

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

if __name__ == '__main__':
    unittest.main()
