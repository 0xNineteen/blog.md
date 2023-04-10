# radix tree which builds a tree of chars
from dataclasses import dataclass

@dataclass
class Node: 
    key: str
    value: any 
    children: list[any] # list[Node]
    parent: any # Node

TREE = Node(None, None, [], None)

def insert(key: str, value: any):
    print(f'COMMAND: insert({key}, {value})')
    _insert(TREE, key, value)
    print('')

def common_substring(s1, s2): 
    for i in range(min(len(s1), len(s2))): 
        if s1[i] != s2[i]: 
            return i

def _insert(node: Node, key: str, value: any):
    # handles initial inserts '1'
    if node.key == None: 
        node.key = key
        node.value = value
        print(f'setting node value ({node.key}, {node.value})')
        return 
    
    # handles updates (insert '2')
    if node.key == key: 
        print(f'updating node value (k {node.key}): {node.value} -> {value}')
        node.value = value
        return # end

    # handles adding a child or parent
    # ensure its a sub or super string
    key_is_sub_string = key in node.key 
    key_is_super_string = node.key in key

    # common_count = common_substring(key, node.key)
    # contains_common = common_count > 0

    assert key_is_sub_string or key_is_super_string # or contains_common
    
    # either 
    #   insert '123' in '12'
    #   check if '3' is substring of another node
    if key_is_super_string: 
        child_chars = key[len(node.key):]

        # grow tree downwards from here 
        child_dne = True
        for child_node in node.children: 
            if child_chars in child_node.key or child_node.key in child_chars: 
                child_dne = False
                break 
        
        if child_dne: 
            print(f'creating new child for {node.key}: ({child_chars})')
            new_node = Node(child_chars, value, [], node)
            node.children.append(new_node)
        else: 
            _insert(child_node, child_chars, value)

    elif key_is_sub_string: 
        # OR
        #   insert '3' (key) in '34' (node.key) THEN
            # parent => node  
            # changes to: parent => new_node('3') => node('4')
        print(f"{key} is substring of {node.key}")

        parent: Node = node.parent 
        # update parent
        child_index = [True if child.key == node.key else False for child in node.parent.children].index(True)
        del parent.children[child_index]

        # update current node
        new_node = Node(key, value, [node], node.parent)
        node.parent = new_node
        node.key = node.key[len(key):]

        # update parent
        parent.children.append(new_node)
    
    # elif contains_common: 
    #     # insert e3344 when root = e3311
    #     # e33 => [44, 11]

if __name__ == "__main__":
    insert('12', 1)
    assert(TREE.key == '12')
    assert(TREE.value == 1)

    # child
    insert('1234', 1)
    assert(TREE.children[0].key == '34')
    assert(TREE.children[0].value == 1)

    # new parent
    # TREE: 12 -> 3 -> 4
    insert('123', 21)
    assert(TREE.children[0].key == '3')
    assert(TREE.children[0].value == 21)

    assert(TREE.children[0].children[0].key == '4')
    assert(TREE.children[0].children[0].value == 1)

    # TREE: 12 -> 3 -> 4
    #          -> abc
    insert('12abc', 24)
    assert(TREE.children[1].key == 'abc')
    assert(TREE.children[1].value == 24)

## ---

def lookup(key: str) -> any:
    print(f'COMMAND: lookup {key}...')
    result = _lookup(TREE, key)
    print('---')
    return result

def _lookup(node: Node, key: str) -> any:
    if node.key == key: 
        print(f'found: {key, node.value}')
        return node.value

    # handles adding a child or parent
    # ensure its a sub or super string
    # lookup '123' in tree: '12' -> '3' -- node.key is substring
    key_is_super_string = node.key in key
    assert key_is_super_string

    child_chars = key[len(node.key):]
    print(f'traversing for {child_chars}...')

    # grow tree downwards from here 
    child_dne = True
    for child_node in node.children: 
        if child_node.key in child_chars: 
            child_dne = False
            break 

    if child_dne: 
        return None
    else: 
        return _lookup(child_node, child_chars)

if __name__ == "__main__":
    assert lookup("12") == 1
    assert lookup("1234") == 1
    assert lookup("123") == 21

    print('success')