from bsttree import BSTTree
from node import Node


class AVLTree(BSTTree):
    def __init__(self):
        super().__init__()

    def delete(self, node: Node, animate: bool = False):
        self._rec_delete(self.root, node, animate)
        self._update_depth(self.root, 0)

    def _rec_delete(self, root, node, animate: bool = False):
        if animate:
            self.animation_focus(root)
        if not root:
            return root
        elif node.value > root.value:
            root.left = self._rec_delete(root.left, node, animate)
        elif node.value < root.value:
            root.right = self._rec_delete(root.right, node, animate)
        else:
            if root.left is None:
                temp = root.right
                del root
                return temp
            elif root.right is None:
                temp = root.left
                del root
                return temp
            temp = self.successor(root)
            root.value = temp.value
            root.right = self._rec_delete(root.right, temp, animate)

        if root is None:
            return root
        balance = self.calc_balance_factor(root)

        self._update_depth(self.root, 0)
        if animate:
            self.animation_focus(root)
        if balance > 1 and self.calc_balance_factor(root.left) >= 0:
            return self.rotate_right(root)
        if balance < -1 and self.calc_balance_factor(root.right) <= 0:
            return self.rotate_left(root)
        if balance > 1 and self.calc_balance_factor(root.left) < 0:
            root.left = self.rotate_left(root.left)
            return self.rotate_right(root)
        if balance < -1 and self.calc_balance_factor(root.right) > 0:
            root.right = self.rotate_right(root.right)
            return self.rotate_left(root)

        return root

    def calc_balance_factor(self, node: Node):
        if node is None:
            return 0
        return self.height(node.left) - self.height(node.right)

    def height(self, node: Node):
        if node is None:
            return 0
        return 1 + max(self.height(node.left), self.height(node.right))

    def insert(self, node: Node, animate: bool = False):
        if self.root is None:
            self.root = node
        else:
            self._rec_insert(self.root, node, animate)
        self._update_depth(self.root, 0)

    def _rec_insert(self, root, node, animate: bool = False):
        if animate:
            self.animation_focus(root)
        if not root:
            return node
        elif node.value > root.value:
            root.left = self._rec_insert(root.left, node, animate)
        else:
            root.right = self._rec_insert(root.right, node, animate)
        balance = self.calc_balance_factor(root)

        self._update_depth(self.root, 0)
        if animate:
            self.animation_focus(root)
        if balance > 1 and node.value > root.left.value:
            return self.rotate_right(root) # problem with root deleting everything
        if balance < -1 and node.value < root.right.value:
            return self.rotate_left(root)
        if balance > 1 and node.value < root.left.value:
            root.left = self.rotate_left(root.left)
            return self.rotate_right(root)
        if balance < -1 and node.value > root.right.value:
            root.right = self.rotate_right(root.right)
            return self.rotate_left(root)
        return root

    def rotate_left(self, z):
        y = z.right
        temp = y.left
        y.left = z
        z.right = temp
        if z is self.root:
            self.root = y
        return y

    def rotate_right(self, z):
        y = z.left
        temp = y.right
        y.right = z
        z.left = temp
        if z is self.root:
            self.root = y
        return y
