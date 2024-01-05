from typing import Callable, Any
from node import Node
import time


class OrderType:
    PREORDER = 0
    INORDER = 1
    POSTORDER = 2


class BSTTree:
    def __init__(self):
        self.root = None
        self.active_node = None
        self.anim_time = .5

    def search(self, value, animate: bool = False):
        return self._rec_search(self.root, value, animate)

    def _rec_search(self, node: Node, value, animate: bool = False):
        if animate:
            self.animation_focus(node)
        if node is None or value == node.value:
            return node
        elif node.value < value:
            return self._rec_search(node.left, value, animate)
        elif node.value > value:
            return self._rec_search(node.right, value, animate)

    def maximum(self, node: Node):
        while node.right is not None:
            node = node.right
        return node

    def minimum(self, node: Node):
        while node.left is not None:
            node = node.left
        return node

    def successor(self, node: Node):
        if node.right is not None:
            return self.minimum(node.right)
        temp = node.parent
        while temp is not None and node == temp.right:
            node = temp
            temp = temp.parent
        return temp

    def predecessor(self, node: Node):
        if node.left is not None:
            return self.maximum(node.left)
        temp = node.parent
        while temp is not None and node == temp.left:
            node = temp
            temp = temp.parent
        return temp

    def insert(self, node: Node, animate: bool = False):
        y = None
        x = self.root
        depth = 0
        while x is not None:
            y = x
            if animate:
                self.animation_focus(y)
            if node.value > x.value:
                x = x.left
            elif node.value < x.value:
                x = x.right
            else:
                return
            depth += 1

        node.parent = y
        node.depth = depth
        if y is None:
            self.root = node
        elif node.value > y.value:
            y.left = node
        else:
            y.right = node

    def delete(self, node: Node, animate: bool = False):
        if animate:
            self.animation_focus(node)
        if node.left is None and node.right is None:
            if node.parent.left is node:
                node.parent.left = None
            else:
                node.parent.right = None
            return
        if node.left is None:
            self._shift_nodes(node, node.right, animate)
        elif node.right is None:
            self._shift_nodes(node, node.left, animate)
        else:
            temp = self.successor(node)
            if temp.parent is not node:
                self._shift_nodes(temp, temp.right, animate)
                temp.right = node.right
                temp.right.parent = temp
            self._shift_nodes(node, temp, animate)
            temp.left = node.left
            temp.left.parent = temp
        self._update_depth(self.root, 0)

    def _shift_nodes(self, u: Node, v: Node, animate: bool = False):
        if animate:
            self.animation_focus(u)
        if u.parent is None:
            self.root = v
        elif u == u.parent.left:
            u.parent.left = v
        else:
            u.parent.right = v
        if v is not None:
            v.parent = u.parent

    def traverse(self, operation: Callable[[Node], Any], order_type: int = OrderType.INORDER, animate: bool = False):
        if animate:
            self.animation_focus(self.root)
        if self.root is not None:
            if order_type == OrderType.PREORDER:
                operation(self.root)
                if animate:
                    self.animation_focus(self.root)
            self._rec_traverse(self.root.left, operation, order_type)
            if order_type == OrderType.INORDER:
                operation(self.root)
                if animate:
                    self.animation_focus(self.root)
            self._rec_traverse(self.root.right, operation, order_type)
            if order_type == OrderType.POSTORDER:
                operation(self.root)
                if animate:
                    self.animation_focus(self.root)

    def _rec_traverse(self, node: Node, operation: Callable[[Node], Any], order_type: int = OrderType.INORDER, animate: bool = False):
        if node is not None:
            if order_type == OrderType.PREORDER:
                operation(node)
                if animate:
                    self.animation_focus(node)
            self._rec_traverse(node.left, operation, order_type)
            if order_type == OrderType.INORDER:
                operation(node)
                if animate:
                    self.animation_focus(node)
            self._rec_traverse(node.right, operation, order_type)
            if order_type == OrderType.POSTORDER:
                operation(node)
                if animate:
                    self.animation_focus(node)

    def _update_depth(self, node: Node, depth: int):
        if node is not None:
            node.depth = depth
            self._update_depth(node.left, depth + 1)
            self._update_depth(node.right, depth + 1)

    def animation_focus(self, node: Node):
        self.active_node = node
        time.sleep(self.anim_time)
        # self.active_node = None


if __name__ == '__main__':  # tester
    t = BSTTree()
    for v in [5, 4, 1, 2, 7, 8, 6, 3]:
        t.insert(Node(v))

    def f(n: Node):
        print(n.value, end=", ")
    print("PREORDER")
    t.traverse(f, OrderType.PREORDER)
    print("\nINORDER")
    t.traverse(f, OrderType.INORDER)
    print("\nPOSTORDER")
    t.traverse(f, OrderType.POSTORDER)
    print("\nDELETE 7")
    t.delete(t.search(7))
    print("POSTORDER")
    t.traverse(f, OrderType.POSTORDER)

    print("\nMAXIMUM")
    print(t.maximum(t.root).value)
    print("MINIMUM")
    print(t.minimum(t.root).value)
    print("SUCCESSOR 5")
    print(t.successor(t.search(5)).value)
    print("PREDECESSOR 4")
    print(t.predecessor(t.search(4)).value)
