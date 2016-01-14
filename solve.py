import sys
from collections import defaultdict


class Server(object):
    def __init__(self, id, size, capacity):
        self.id = id
        self.size = size
        self.capacity = capacity
        self.row = None
        self.slot = None
        self.pool = None

    def __repr__(self):
        return "server-{id} size: {size} cap: {capacity} score: {score:.2} pool: {pool}".format(
            id=self.id,
            size=self.size,
            row=self.row,
            slot=self.slot,
            pool=self.pool,
            capacity=self.capacity,
            score=self.score)

    @property
    def score(self):
        return self.capacity / float(self.size)


class Segment(object):
    def __init__(self, slots, slot):
        self.slots = slots
        self.slot = slot


class Row(object):
    def __init__(self, id, npools, segments):
        self.id = id
        self.segments = segments
        self.servers = []
        self.score = npools * [0]

    def __repr__(self):
        return 'Row' + str(self.id) + ', '.join(map(str, self.servers))


class DataCenter(object):
    def __init__(self, nrows, nslots, npools, unavailables, rows):
        self.nrows = nrows
        self.nslots = nslots
        self.npools = npools
        self.rows = rows

        self.capacity_total = self.npools * [0]
        self.capacity_row_pool = self.nrows * [None]
        for row in xrange(self.nrows):
            self.capacity_row_pool[row] = self.npools * [0]

    def __repr__(self):
        print self.rows
        return '\n'.join(map(lambda x: str(x), self.rows))

    def try_place_row(self, server, row, pool):
        for i, segment in enumerate(row.segments):
            print 'try place server [', server, '] on row', row.id, 'segment', i, 'limit', segment.slots, 'slot', segment.slot, 'having pool', pool
            if server.size <= segment.slots:
                self.place_row(server, row, segment, pool)
                print 'success'
                return True
            print 'failure'
        return False

    def place_row(self, server, row, segment, pool):
        server.row = row.id
        server.slot = segment.slot
        segment.slot += server.size
        server.pool = pool
        segment.slots -= server.size
        if segment.slots == 0:
            row.segments.remove(segment)
        row.servers.append(server)
        row.score[pool] += server.capacity
        self.capacity_total[pool] += server.capacity
        self.capacity_row_pool[row.id][pool] += server.capacity

    def find_min_pool(self, servers):
        min_pool = sys.maxint
        min_value = sys.maxint
        for row in xrange(self.nrows):
            for pool in xrange(self.npools):
                tmp = self.capacity_total[pool] - self.capacity_row_pool[row][pool]
                if tmp < min_value:
                    min_value = tmp
                    min_pool = pool

        return min_pool, min_value

    def solve(self, servers):
        # sort servers by descending score and descending size
        _servers = sorted(
            servers,
            key=lambda x: (x.score, x.size), reverse=True)
        while len(_servers) > 1:
            server = _servers.pop(0)
            pool, _ = self.find_min_pool(_servers)
            # sort rows by score of selected pool
            self.rows.sort(
                key=lambda x: (x.score[pool]))
            for row in self.rows:
                success = self.try_place_row(server, row, pool)
                if success:
                    break

        print self.find_min_pool(servers)


def main(path):
    with open(path, 'r') as handle:
        unavailables = defaultdict(list)

        (n_rows, n_slots, n_unavailable, n_pools, n_servers) = [int(n)
                                                                for n
                                                                in handle.next().strip().split(' ')]

        rows = []
        for i in range(n_unavailable):
            (x, y) = [int(n) for n in handle.next().strip().split(' ')]
            unavailables[x].append(y)

        for i in range(n_rows):
            segments = []
            if i in unavailables:
                for start, size in split_row(n_slots, unavailables[x]):
                    segments.append(Segment(size, start))
            else:
                segments = [Segment(n_slots, 0)]
            rows.append(Row(i, n_pools, segments))

        datacenter = DataCenter(n_rows, n_slots, n_pools, unavailables, rows)
        servers = []
        for i in range(n_servers):
            (slots, capacity) = [int(n) for n in handle.next().strip().split(' ')]
            servers.append(Server(i, slots, capacity))

        datacenter.solve(servers)
        print_solution(servers)


def print_solution(servers):
    with open('out', 'w') as out:
        _servers = sorted(servers, key=lambda x: x.id)
        for server in _servers:
            if server.row < 0:
                out.write('x\n')
            else:
                out.write('{row} {slot} {pool}\n'.format(row=server.row,
                                                         slot=server.slot,
                                                         pool=server.pool))


def split_row(slots, unavailables):
    row = []

    size = 0
    i0 = 0
    for i in range(slots):
        if i in unavailables:
            if size > 0:
                row.append((i0, size))
            i0 = i + 1
            size = 0
        else:
            size += 1
    if size > 0:
        row.append((i0, size))
    return row


if __name__ == '__main__':
    path = sys.argv[1]
    main(path)
