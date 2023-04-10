from dataclasses import dataclass

@dataclass
class Node: 
    key: str
    value: any 
    children: any # list[Node]

TREE = Node(None, None, [])

def insert(key: str, value: any):
    _insert(TREE, key, value)
    print('---')

def _insert(node: Node, key: str, value: any):
    char = key[0]
    rest = key[1:]

    # handles initial inserts '1'
    if node.key == None: 
        node.key = char 
    
    # handles updates (insert '2')
    if len(rest) == 0: 
        if node.key != char: 
            print(f"{node.key} {char}")
            raise NotImplementedError 
        else: 
            print(f'updating node value (k {node.key}): {node.value} -> {value}')
            node.value = value
        return # end

    # handles adding a child
    assert node.key == char
    
    child_char = rest[0]

    # if char exists as a child
    child_dne = True
    for child_node in node.children: 
        if child_node.key == child_char: 
            child_dne = False
            break 
        
    if child_dne: 
        child_node = Node(child_char, None, [])
        node.children.append(child_node)

    print(f'traversing node: {node.key}')
    _insert(child_node, rest, value)


insert('1', 1)
assert(TREE.key == '1')
assert(TREE.value == 1)

insert('1', 2)
assert(TREE.key == '1')
assert(TREE.value == 2)

insert('12', 12)
assert TREE.key == '1'
assert TREE.children[0].key == '2'
assert TREE.children[0].value == 12

insert('123', 123)
assert(TREE.children[0].children[0].key == '3')
assert(TREE.children[0].children[0].value == 123)

insert('1a', 124)
assert(TREE.children[1].key == 'a')
assert(TREE.children[1].value == 124)

## ---

def lookup(key: str) -> any:
    print('---')
    return _lookup(TREE, key)

def _lookup(node: Node, key: str) -> any:
    char = key[0]
    rest = key[1:]

    # assert were on the right path
    assert char == node.key
    if len(rest) == 0: 
        return node.value

    child_char = rest[0]
    
    child_dne = True
    for child_node in node.children: 
        if child_node.key == child_char: 
            child_dne = False
            break 

    if child_dne: 
        return None
    
    return _lookup(child_node, rest)

assert lookup("1a") == 124
assert lookup("123") == 123
assert lookup("12") == 12
assert lookup("1") == 2

print('success')