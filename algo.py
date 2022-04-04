from pprint import pprint
# c-spell: ignore ospf inet dgram sendto

def ospf_algo(tables):
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


def rip_new_table(current_table, my_ip, new_table, new_table_src):
    all_dst = set()
    for dst in current_table:
        all_dst.add(dst)
    for dst in new_table:
        all_dst.add(dst)
    all_dst.remove(my_ip)

    result = {}

    for dst in all_dst:
        current_min = 99999999
        best_next_hop = None
        for this_dst, (next_hop, cost) in current_table.items():
            if this_dst == dst and cost < current_min:
                current_min = cost
                best_next_hop = next_hop

        cost_of_me_to_new_table_src = current_table[new_table_src][1]
        # cost_of_me_to_new_table_src = current_table.get(new_table_src, (0, 1))[1]
        for this_dst, (next_hop, cost) in new_table.items():
            if this_dst == dst and cost + cost_of_me_to_new_table_src < current_min:
                current_min = cost + cost_of_me_to_new_table_src
                best_next_hop = new_table_src

        assert best_next_hop is not None
        result[dst] = (best_next_hop, current_min)

    if result == current_table:
        return None

    return result


if __name__ == '__main__':
    table1 = {
        'r1': {
            'h1': ('h1', 1),
            'h2': ('h2', 1),
            'r2': ('r2', 1),
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


    assert ospf_algo(table1) == \
    {'r1': {'h1': ('h1', 1), 'h2': ('h2', 1), 'h3': ('r2', 2), 'h4': ('r2', 2)},
     'r2': {'h1': ('r1', 2), 'h2': ('r1', 2), 'h3': ('h3', 1), 'h4': ('h4', 1)}}

    assert rip_new_table(table1['r1'], 'r1', table1['r2'], 'r2') == \
        {'h1': ('h1', 1),
        'h2': ('h2', 1),
        'h3': ('r2', 2),
        'h4': ('r2', 2),
        'r2': ('r2', 1)}
    assert rip_new_table(table1['r2'], 'r2', table1['r1'], 'r1') == \
        {'h1': ('r1', 2),
        'h2': ('r1', 2),
        'h3': ('h3', 1),
        'h4': ('h4', 1),
        'r1': ('r1', 1)}

    # graph: https://imgur.com/a/WIMfiQf
    # From tut 07 Q4
    table3 = {
        'u': { 'v': ('v', 1), 'y': ('y', 2) },
        'v': { 'u': ('u', 1), 'z': ('z', 6), 'x': ('x', 3) },
        'z': { 'v': ('v', 6), 'x': ('x', 2) },
        'z': { 'v': ('v', 6), 'x': ('x', 2) },
        'x': { 'v': ('v', 3), 'z': ('z', 2), 'y': ('y', 3) },
        'y': { 'u': ('u', 2), 'x': ('x', 3) },
    }

    nodes = list(table3.keys())
    neighbors = { node: table3[node].keys() for node in nodes }

    # tuple: update_for, update_from, update_table
    update_queue = [(n, nodes[0], table3[nodes[0]]) for n in neighbors[nodes[0]]]

    for update in update_queue:
        update_for, update_from, update_table = update
        updated_table = rip_new_table(table3[update_for], update_for, table3[update_from], update_from)
        if updated_table is not None:
            table3[update_for] = updated_table
            for neighbor in neighbors[update_for]:
                update_queue.append((neighbor, update_for, updated_table))

    assert table3 == \
    {'u': {'v': ('v', 1), 'x': ('v', 4), 'y': ('y', 2), 'z': ('v', 6)},
    'v': {'u': ('u', 1), 'x': ('x', 3), 'y': ('u', 3), 'z': ('x', 5)},
    'x': {'u': ('v', 4), 'v': ('v', 3), 'y': ('y', 3), 'z': ('z', 2)},
    'y': {'u': ('u', 2), 'v': ('u', 3), 'x': ('x', 3), 'z': ('x', 5)},
    'z': {'u': ('x', 6), 'v': ('x', 5), 'x': ('x', 2), 'y': ('x', 5)}}

