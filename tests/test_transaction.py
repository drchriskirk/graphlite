from graphlite import V
from sqlite3 import OperationalError
from threading import Thread


def threading_test(function, iterable):
    threads = [Thread(target=function(x)) for x in iterable]

    [thread.start() for thread in threads]
    [thread.join() for thread in threads]


def test_concurrency(graph):
    stored = [V(1).knows(i) for i in range(5, 9)]

    def store(value):
        def callback():
            with graph.transaction() as tr:
                tr.store(value)
        return callback

    threading_test(store, stored)
    for item in stored:
        assert item in graph


def test_transaction(graph):
    with graph.transaction() as tr:
        tr.store(V(1).knows(7))
        tr.store(V(1).knows(8))

    assert V(1).knows(7) in graph
    assert V(1).knows(8) in graph


def test_transaction_atomic(graph):
    try:
        with graph.transaction() as tr:
            tr.store(V(1).knows(7))
            tr.store(V(1).does(1))
        raise AssertionError
    except OperationalError:
        assert V(1).knows(7) not in graph


def test_delete(graph):
    queries = [
        V(1).knows(2),
        V().knows(3),
        V().knows,
    ]
    assertions = [
        lambda: V(1).knows(2) not in graph,
        lambda: V(1).knows(3) not in graph,
        lambda: V(1).knows(4) not in graph,
    ]

    for assertion, query in zip(assertions, queries):
        with graph.transaction() as tr:
            tr.delete(query)

        assert assertion()
