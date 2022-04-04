# c-spell: ignore ospf inet dgram sendto

def ospf_algo(tables):
    print(tables)
    adjacency_list = {}
    routers = list(tables.keys())
    hosts = [x for y in tables.values() for x in y.keys() if x not in routers]
    result = { router: {} for router in routers }

    for router, routing_table in tables.items():
        for dst, (next_hop, cost) in routing_table.items():
            if cost != 1: continue # Skip non-neighbor entries
            if dst in adjacency_list:
                adjacency_list[dst].append(router)
            else:
                adjacency_list[dst] = [router]

    for host in hosts:
        for neighbor in adjacency_list.get(host, []):
            ospf_bfs(adjacency_list, result, host, host, neighbor, 1)

    return result

def ospf_bfs(adjacency_list, result, dst, prev_hop, current_hop, hops):
    if result[current_hop].get(dst, (0, 99999999))[1] < hops:
        return
    result[current_hop][dst] = (prev_hop, hops)
    for neighbor in adjacency_list.get(current_hop, []):
        ospf_bfs(adjacency_list, result, dst, current_hop, neighbor, hops + 1)

if __name__ == '__main__':
    table = {
        'r1': {
            'h1': ('h1', 1),
            'h2': ('h2', 1),
            'r2': ('r2', 1),
            'r3': ('r3', 1),
        },
        'r2': {
            'h3': ('h3', 1),
            'r1': ('r1', 1),
            'h4': ('h4', 1)
        },
    }

    table2 = {
        'r1': {
            'h1': ('h1', 1),
            'r2': ('r2', 1),
            'r3': ('r3', 1),
        },
        'r2': {
            'r1': ('r1', 1),
            'h2': ('h2', 1),
            'r3': ('r3', 1),
        },
        'r3': {
            'r1': ('r1', 1),
            'r2': ('r2', 1),
            'h3': ('h3', 1),
        },
    }

    from pprint import pprint
    pprint(ospf_algo(None, table2))
