import edmv
import sys
import io


def run_trial(trial):
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

    def test_mv(src, dest):
        src = strip_uuid(src)
        dest = strip_uuid(dest)
        if 'ERROR' in (src, dest):
            print(src, "=>", dest, "[simulating error]")
            raise Exception("Simulated error")
        else:
            print(src, "=>", dest)

    stderr = sys.stderr
    stdout = sys.stdout
    try:
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()
        if edmv.edmv(sources, editor = test_editor, mv = test_mv):
            print("Pass", file=sys.stderr)
        else:
            print("Fail", file=sys.stderr)
        return sys.stdout.getvalue(), sys.stderr.getvalue()
    finally:
        sys.stderr = stderr
        sys.stdout = stdout

def assert_trial(trial, expected_stdout_lines, expected_stderr=''):
    out, err = run_trial(trial)

    expected_stdout = '\n'.join(expected_stdout_lines)

    if out.strip() != expected_stdout.strip():
        raise AssertionError("Expected\n" + expected_stdout + "\nGot\n" + out)
    if err.strip() != expected_stderr.strip():
        raise AssertionError("Expected\n" + expected_stderr + "\nGot\n" + err)

print("Test: normal renaming")
assert_trial((
        ('a', 'b'),
        ('c', 'c')
), (
        "a => b",
), "Pass")

print("Test: cycling renaming")
assert_trial((
        ('a', 'b'),
        ('b', 'a')
), (
        "a => b.[UUID].edmv",
        "b => a.[UUID].edmv",
        "b.[UUID].edmv => b",
        "a.[UUID].edmv => a",
), "Pass")

print("Test: mixture")
assert_trial((
        ('a', 'b'),
        ('b', 'c'),
        ('c', 'a'),
        ('1', '1'),
        ('2', '3'),
), (
    "a => b.[UUID].edmv",
    "b => c.[UUID].edmv",
    "c => a.[UUID].edmv",
    "2 => 3",
    "b.[UUID].edmv => b",
    "c.[UUID].edmv => c",
    "a.[UUID].edmv => a",
), "Pass")

print("Test: fail and undo")
assert_trial((
        ('a', 'b'),
        ('b', 'c'),
        ('c', 'a'),
        ('1', '1'),
        ('2', '3'),
        ('5', 'ERROR'),
        ('6', '7'),
), (
        "a => b.[UUID].edmv",
        "b => c.[UUID].edmv",
        "c => a.[UUID].edmv",
        "2 => 3",
        "5 => ERROR [simulating error]",
        "3 => 2",
        "a.[UUID].edmv => c",
        "c.[UUID].edmv => b",
        "b.[UUID].edmv => a",
), "Error: Simulated error\nUndoing...\nFail")
