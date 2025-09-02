from __future__ import annotations
import json
from math import ceil, floor
from typing import List

# Node Class.
# You may make minor modifications.
class Node():
    def  __init__(self,
                  keys     : List[int]  = None,
                  values   : List[str] = None,
                  children : List[Node] = None,
                  parent   : Node = None):
        self.keys     = keys
        self.values   = values
        self.children = children
        self.parent   = parent

# DO NOT MODIFY THIS CLASS DEFINITION.
class Btree():
    def  __init__(self,
                  m    : int  = None,
                  root : Node = None):
        self.m    = m
        self.root = root

    # DO NOT MODIFY THIS CLASS METHOD.
    def dump(self) -> str:
        def _to_dict(node) -> dict:
            return {
                "keys": node.keys,
                "values": node.values,
                "children": [(_to_dict(child) if child is not None else None) for child in node.children]
            }
        if self.root == None:
            dict_repr = {}
        else:
            dict_repr = _to_dict(self.root)
        return json.dumps(dict_repr,indent=2)
    

    # Insert.
    def insert(self, key: int, value: str):
        if(self.root == None):
            self.root = Node([], [], [None], None)
        if self.root.children == None:
            self.root.children = [None]
        
        def left_rotation(left: Node, curr: Node, p_index: int):
            count = len(left.keys) + self.m # total number of keys in both
            c_count = self.m
            if len(left.keys) >= self.m - 1: # no space in right node
                return 0
            def left_rotate_helper():
                if len(left.keys) == self.m-1:
                    return 1
                left.keys.append(curr.parent.keys[p_index - 1])
                left.values.append(curr.parent.values[p_index - 1])
                left.children.append(curr.children[0])
                if curr.children[0] != None:
                    curr.children[0].parent = left
                curr.parent.keys[p_index-1] = curr.keys[0]
                curr.parent.values[p_index-1] = curr.values[0]
                curr.keys.remove(curr.keys[0])
                curr.values.remove(curr.values[0])
                curr.children.remove(curr.children[0])
                return 0
            is_full = 0
            while((c_count > ceil(count/2)) & (is_full == 0)):
                is_full = left_rotate_helper()
                c_count -= 1
            return 1

        def right_rotation(curr: Node, right: Node, p_index: int):
            count = len(right.keys) + self.m # total number of keys in both
            c_count = self.m
            if len(right.keys) >= self.m - 1: # no space in right node
                return 0
            def right_rotate_helper():
                if len(right.keys) == self.m-1:
                    return 1
                right.keys.insert(0, curr.parent.keys[p_index])
                right.values.insert(0, curr.parent.values[p_index])
                right.children.insert(0, curr.children[len(curr.children)-1])
                if curr.children[0] != None:
                    curr.children[len(curr.children)-1].parent = right
                curr.parent.keys[p_index] = curr.keys[len(curr.keys)-1]
                curr.parent.values[p_index] = curr.values[len(curr.values)-1]
                curr.keys.remove(curr.keys[len(curr.keys)-1])
                curr.values.remove(curr.values[len(curr.values)-1])
                curr.children.remove(curr.children[len(curr.children)-1])
                return 0
            is_full = 0
            while((c_count > ceil(count/2)) & (is_full == 0)):
                is_full = right_rotate_helper()
                c_count -= 1
            return 1
        
        def split(curr: Node, parent: Node, p_index):
            median: int = ceil(len(curr.keys)/2) - 1
            L_Node = Node(curr.keys[:median], curr.values[:median], curr.children[:median+1], parent)
            R_Node = Node(curr.keys[median+1:], curr.values[median+1:], curr.children[median+1:], parent)
            index = 0
            if curr.children[0] != None:
                while index < len(curr.children):
                    if(index < median+1):
                        curr.children[index].parent = L_Node
                    else:
                        curr.children[index].parent = R_Node
                    index += 1
            if(parent == None):
                P_Node = Node([curr.keys[median]], [curr.values[median]], [L_Node,R_Node], None)
                self.root = P_Node
                L_Node.parent = P_Node
                R_Node.parent = P_Node
                return 1
            else:
                parent.keys.insert(p_index, curr.keys[median])
                parent.values.insert(p_index, curr.values[median])
                parent.children[p_index] = L_Node
                parent.children.insert(p_index+1, R_Node)
                return 0

        def fix_overfull(node: Node):
            if len(node.keys) == self.m: # node is overfull
                valid = 0
                index = 0
                if(node != self.root):
                    index = node.parent.children.index(node)
                    if index != 0:
                        valid = left_rotation(node.parent.children[index-1], node, index)
                    if valid == 0:
                        if index != len(node.parent.children) - 1:
                            valid = right_rotation(node, node.parent.children[index+1], index)
                if valid == 0:
                    is_root = split(node, node.parent, index)
                    if is_root == 0:
                        fix_overfull(node.parent)
            
        # Fill in the details.
        def insert_helper(node: Node):
            if node.children[0] == None: # if this is a leaf node
                index: int = 0
                while index < len(node.keys):
                    if key < node.keys[index]:
                        break
                    index += 1
                node.keys.insert(index, key)
                node.values.insert(index, value)
                node.children.append(None)
                fix_overfull(node)
                return

            index = 0
            while index < len(node.keys): # find the right leaf node for key
                if key < node.keys[index]:
                    break
                index += 1
            insert_helper(node.children[index])

        insert_helper(self.root)
        
                

    # Delete.
    def delete(self, key: int):
        def find_replacement(node: Node):
            if(node.children[0] == None):
                return (node.keys[0], node.values[0])
            else:
                return find_replacement(node.children[0])
            
        def right_rotate(left: Node, curr: Node, p_index: int):
            count = len(left.keys) + ceil(self.m/2) - 2 # total number of keys in both
            c_count = ceil(self.m/2) - 2
            if len(left.keys) <= ceil(self.m/2) - 1: # no space in right node
                return 0
            def right_rotate_helper():
                if len(left.keys) <= ceil(self.m/2) - 1:
                    return 1
                curr.keys.insert(0, curr.parent.keys[p_index-1])
                curr.values.insert(0, curr.parent.values[p_index-1])
                curr.children.insert(0, left.children[len(left.children)-1])
                if curr.children[0] != None:
                    left.children[len(left.children)-1].parent = curr
                curr.parent.keys[p_index-1] = left.keys[len(left.keys)-1]
                curr.parent.values[p_index-1] = left.values[len(left.values)-1]
                left.keys.remove(left.keys[len(left.keys)-1])
                left.values.remove(left.values[len(left.values)-1])
                left.children.remove(left.children[len(left.children)-1])
                return 0
            is_empty = 0
            while((c_count < floor(count/2)) & (is_empty == 0)):
                is_empty = right_rotate_helper()
                c_count += 1
            return 1
        
        def left_rotate(curr: Node, right: Node, p_index: int):
            count = len(right.keys) + ceil(self.m/2) - 2 # total number of keys in both
            c_count = ceil(self.m/2) - 2
            if len(right.keys) <= ceil(self.m/2) - 1: # no space in right node
                return 0
            def left_rotate_helper():
                if len(right.keys) <= ceil(self.m/2) - 1:
                    return 1
                curr.keys.append(curr.parent.keys[p_index])
                curr.values.append(curr.parent.values[p_index])
                curr.children.append(right.children[0])
                if curr.children[0] != None:
                    right.children[0].parent = curr
                curr.parent.keys[p_index] = right.keys[0]
                curr.parent.values[p_index] = right.values[0]
                right.keys.remove(right.keys[0])
                right.values.remove(right.values[0])
                right.children.remove(right.children[0])
                return 0
            is_empty = 0
            while((c_count < floor(count/2)) & (is_empty == 0)):
                is_empty = left_rotate_helper()
                c_count += 1
            return 1
        
        def merge(left: Node, right: Node, index: int):
            N_Node = Node(left.keys+[left.parent.keys[index-1]]+right.keys, 
                          left.values+[left.parent.values[index-1]]+right.values, 
                          left.children+right.children, left.parent)
            N_Node.parent.children[N_Node.parent.children.index(left)] = N_Node
            N_Node.parent.children.remove(right)
            N_Node.parent.keys.remove(N_Node.parent.keys[index-1])
            N_Node.parent.values.remove(N_Node.parent.values[index-1])
            if(N_Node.children[0] != None):
                for n in N_Node.children:
                    n.parent = N_Node
            if len(self.root.keys) == 0:
                self.root = N_Node
                N_Node.parent = None

            
        
        def fix_underfull(node: Node):
            if node == self.root:
                return
            if node == None:
                return
            odd = self.m%2
            if len(node.keys) >= ((self.m+odd)/2) - 1:
                return
            valid = 0
            if node.parent != None:
                index = node.parent.children.index(node)
                if index != 0:
                    valid = right_rotate(node.parent.children[index-1], node, index)
                if valid == 0:
                    if index != len(node.parent.children) - 1:
                        valid = left_rotate(node, node.parent.children[index+1], index)
                    if valid == 0:
                        if index != 0:
                            merge(node.parent.children[index-1], node, index)
                        else:
                            merge(node, node.parent.children[index+1], index+1)
                        fix_underfull(node.parent)

        def delete_helper(node: Node, key: int):
            if key in node.keys:
                if node.children[0] == None:
                    index = node.keys.index(key)
                    node.keys.remove(key)
                    node.values.remove(node.values[index])
                    node.children.remove(None)
                    fix_underfull(node)
                else:
                    index = node.keys.index(key)
                    (new_key, new_val) = find_replacement(node.children[index+1])
                    node.keys[index] = new_key
                    node.values[index] = new_val
                    delete_helper(node.children[index+1], new_key)
            else:
                index = 0
                while index < len(node.keys):
                    if key < node.keys[index]:
                        break
                    index += 1
                delete_helper(node.children[index], key)
        delete_helper(self.root, key)

    # Search
    def search(self,key) -> str:
        def search_helper(curr: Node, key):
            if key in curr.keys:
                return [curr.values[curr.keys.index(key)]]
            else:
                index = 0
                while index < len(curr.keys):
                    if key < curr.keys[index]:
                        break
                    index += 1
                res = [index]
                res += search_helper(curr.children[index], key)
                return res
        res = search_helper(self.root,key)
        return json.dumps(res)
