# Nikko Rush
# 11/8/2019

import access


class CircularGraphError(Exception):
    pass


class UnknownTargetError(Exception):
    pass


def get_depth_first_ordering(start, nodes, key, child_key, reverse=False):
    visited = set()
    processed = set()
    output = list()

    tree_helper(start, nodes, key, child_key, visited, processed, output)

    return output if reverse else reversed(output)


@access.private
def tree_helper(curr, nodes, key, child_key, visited, processed, output):
    if curr[key] in processed:
        return

    if curr[key] in visited:
        raise CircularGraphError("Encountered a cycle while parsing the graph")

    visited.add(curr[key])

    for child_name in curr.get(child_key, list()):
        child_node = nodes.get(child_name, None)
        if child_node is None:
            raise UnknownTargetException("Unknown target: " + child_name)

        tree_helper(child_node, nodes, key, child_key, visited, processed, output)

    visited.remove(curr[key])
    processed.add(curr[key])
    output.append(curr)
