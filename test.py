import edmv


def run_trial(trial):
    sources = [x[0] for x in trial]

    contents = "\n".join((x[1] for x in trial))
    def test_editor(filename):
        with open(filename, 'w') as f:
            f.write(contents)

    def test_mv(src, dest):
        if 'ERROR' in (src, dest):
            print(src, "=>", dest, "[simulating error]")
            raise Exception("Simulated error")
        else:
            print(src, "=>", dest)

    if edmv.edmv(sources, editor = test_editor, mv = test_mv):
        print("Pass")
    else:
        print("Fail")

run_trial([
    ('a', 'b'),
    ('b', 'c'),
    ('c', 'a'),
    ('1', '1'),
    ('2', '3'),
    ('5', 'ERROR'),
    ('6', '7'),
])
"""
a => b.09aa5f62-11ed-4ca7-855c-68d1d2dfd859.edmv
b => c.bc6d77b5-92d1-45f8-b683-223436ed1f5b.edmv
c => a.d67614ee-b254-42a5-b3fe-ce7a7d876cee.edmv
2 => 3
5 => ERROR [simulating error]
Error: Simulated error
Undoing...
3 => 2
a.d67614ee-b254-42a5-b3fe-ce7a7d876cee.edmv => c
c.bc6d77b5-92d1-45f8-b683-223436ed1f5b.edmv => b
b.09aa5f62-11ed-4ca7-855c-68d1d2dfd859.edmv => a
Fail
"""
