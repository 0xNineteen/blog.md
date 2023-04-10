# radix tree for hex values

from dataclasses import dataclass
import hashlib

@dataclass
class Node: 
    key: str
    value: any 
    children: list[any] # list[Node]

    @staticmethod
    def default(): 
        return Node(None, None, [None] * 16)

    def print(self): 
        print_tree(self)

HEX_VALUES = '0123456789abcdef'

def print_tree(node: Node, indent: str = ""):
    if node.key == None and node.value == None: 
        print('ROOT:')
    else:
        print(indent + str(node.key) + ": " + str(node.value))

    for i, child in enumerate(node.children):
        if child is not None:
            print(f"[{i}]", end='')
            if i < 10: 
                print(" ", end='')
            print_tree(child, indent + "  ")

def ishex(char): 
    return len(char) == 1 and char in HEX_VALUES 

def common_substring(s1, s2): 
    print(f'comparing: {s1} {s2}')
    for i in range(min(len(s1), len(s2))): 
        if s1[i] != s2[i]: 
            return i
    return i + 1

def _insert(node: Node, key: str, value: any):
    char = key[0]
    assert ishex(char)
    v = int(char, 16)

    rest = key[1:]

    # handle initialization
    # insert 'abc'
        # tree -> [('abc')]
    if node.children[v] == None: 
        print('initializing empty...')
        leaf_node = node.default()
        leaf_node.key = key
        leaf_node.value = value
        node.children[v] = leaf_node
        return # exit

    child_node = node.children[v]
    child_key = child_node.key
    assert child_key[0] == char

    # handle updating value
    if key == child_key: 
        print(f'updating node value: {node.value}->{value}')
        child_node.value = value 
        return 

    # update value 
    substring_len = common_substring(key, child_key)
    assert substring_len > 0

    print(f'traversing ... {key} => {rest}')
    if substring_len == len(child_key): 
        rest = key[substring_len:]
        # grow from child 
        _insert(child_node, rest, value)

    elif substring_len == len(key):
        # parent -> new_node
        new_node = Node.default()
        new_node.key = key
        new_node.value = value

        # new_node -> child_node
        child_node.key = child_key[substring_len:]
        char = child_node.key[0]
        new_node.children[int(char, 16)] = child_node

        node.children[v] = new_node
    else: 
        # parent -> new_tmp_node -> [child_node', new_node']

        # parent -> new_tmp_node
        common_substring_ = key[:substring_len]
        print(f'setting up common substring: {common_substring_}...')
        new_tmp_node = node.default()
        new_tmp_node.key = common_substring_
        new_tmp_node.value = None
        node.children[v] = new_tmp_node

        # new_tmp_node -> [new_node']
        new_node = node.default()
        new_node.key = key[substring_len:]
        new_node.value = value
        new_tmp_node.children[int(new_node.key[0], 16)] = new_node

        # new_tmp_node -> [new_node', child_node']
        child_node.key = child_key[substring_len:]
        new_tmp_node.children[int(child_node.key[0], 16)] = child_node

TREE = Node.default()
def insert(key: str, value: any):
    print(f'COMMAND: insert({key}, {value})')
    _insert(TREE, key, value)
    print('')

if __name__ == "__main__":
    insert('a', 1)
    idx = int('a', 16)
    assert TREE.children[idx].key == 'a'
    assert TREE.children[idx].value == 1

    insert('ab', 2)
    assert TREE.children[idx].children[idx+1].key == 'b'
    assert TREE.children[idx].children[idx+1].value == 2

    TREE = Node.default()
    insert('abcd', 1)
    assert TREE.children[idx].key == 'abcd'

    insert('ab', 1)
    assert TREE.children[idx].key == 'ab'
    assert TREE.children[idx].children[int('c', 16)].key == 'cd'

def generate(length = 5): 
    import random
    out = ''
    for _ in range(length): 
        i = random.randint(0, len(HEX_VALUES)-1)
        out += str(HEX_VALUES[i])
    return out

if __name__ == "__main__":
    TREE = Node.default()
    for _ in range(20): 
        x = generate()
        insert(x, 2)

    print_tree(TREE)