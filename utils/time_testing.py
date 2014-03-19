import timeit
import save_data as sd

def find_edges_a():
    edges = sd.session.query(sd.Edge).filter_by(end_a=65314183).all()
    ends = [e.end_b for e in edges]
    edges = sd.session.query(sd.Edge).filter_by(end_b=65314183).all()
    ends += [e.end_a for e in edges]
    return ends

def find_edges_b():
    edges = sd.session.query(sd.Edge).filter((sd.Edge.end_a==65314183)|(sd.Edge.end_b==65314183)).all()
    ends = [e.end_b for e in edges if e.end_a==65314183]
    ends += [e.end_a for e in edges if e.end_b==65314183]
    return ends


if __name__ == '__main__':
    import timeit
    print "a"
    a = timeit.Timer('find_edges_a()', setup='import save_data as sd\nfrom __main__ import find_edges_a')
    print a.timeit(1000)
    b = timeit.Timer('find_edges_b()', setup='import save_data as sd\nfrom __main__ import find_edges_b')
    print b.timeit(1000)