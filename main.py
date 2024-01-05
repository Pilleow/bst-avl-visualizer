import random
import threading
import pygame

from node import Node
from bsttree import BSTTree
from avltree import AVLTree


class ViewMode:
    NONE = ""
    BST = "BST"
    AVL = "AVL"


class InputMode:
    NONE = ""
    INSERT = "INSERT"
    DELETE = "DELETE"
    SEARCH = "SEARCH"
    INFO = ">"


class App:
    def __init__(self, resolution: tuple = (1300, 800), fps: int = 60):
        self.COLOR_NODE_SELECTED = pygame.color.Color(0, 255, 255)
        self.RESOLUTION = pygame.math.Vector2(resolution)
        self.FPS = fps
        self.LINE_COLOR_LEFT = pygame.color.Color(100, 110, 170)
        self.LINE_COLOR_RIGHT = pygame.color.Color(100, 170, 110)
        self.NODE_COLOR_FULL = pygame.color.Color(255, 255, 255)
        self.BG_COLOR = pygame.color.Color(0, 10, 20)
        self.HIGHLIGHTED_COLOR_BST = pygame.color.Color(90, 100, 230)
        self.HIGHLIGHTED_COLOR_AVL = pygame.color.Color(90, 230, 100)
        self.ZOOM_DELTA = 5

        self.depth_height_delta = 80
        self.node_radius = 20
        self.tree_size = 6
        self.x_node_span = 0

        self.input = ""
        self.input_mode = InputMode.NONE
        self.tree_view_mode = ViewMode.BST
        self.view_scroll = pygame.math.Vector2(0, 30)
        self.node_count_per_depth_drawn = {}
        self.bst_node_count_per_depth = {}
        self.avl_node_count_per_depth = {}
        self.node_points = []
        self.mouse_pos = [-100, -100]
        self.lmb_down = False
        self.execute_input = False
        self.recenter_view = False

        self.timer = None
        self.screen = None
        self.node_font = None
        self.help_font = None
        self.help_text = None
        self.input_font = None
        self.initialize_window()

        self.avl_tree = None
        self.bst_tree = None
        self.initialize_trees()

        self.running = True
        while self.running:
            self.main_loop()
        pygame.quit()

    def initialize_window(self):
        pygame.init()
        self.screen = pygame.display.set_mode(self.RESOLUTION)
        pygame.display.set_caption("Wizualizator drzewa BST i AVL")
        img = pygame.image.load("icon.ico").convert_alpha()
        pygame.display.set_icon(img)
        self.timer = pygame.time.Clock()
        self.node_font = pygame.font.Font("Arvo-Bold.ttf", 16 * self.node_radius // 20)
        self.input_font = pygame.font.Font("Arvo-Bold.ttf", 36)
        self.help_font = pygame.font.Font("Arvo-Bold.ttf", 12)
        self.help_text = self.help_font.render("INSERT (I), DELETE (D), SEARCH (S), ZOOM IN (+), ZOOM OUT (-), "
                                               "ADD NODES (UP), REMOVE NODES (DOWN), SLOW DOWN (LEFT), "
                                               "SPEED UP (RIGHT), MOVE (LMB)", True, pygame.color.Color(30, 40, 50))

    def initialize_trees(self):
        self.recenter_view = True
        self._init_avl()
        self._init_bst()
        self.count_nodes_per_depth()

    def _init_avl(self):
        self.avl_tree = AVLTree()
        values = [i for i in range(1, 5 * (self.tree_size + 1), 5)]
        random.shuffle(values)
        for value in values:
            self.avl_tree.insert(Node(value))

    def _init_bst(self):
        self.bst_tree = BSTTree()
        values = [i for i in range(1, 5 * (self.tree_size + 1), 5)]
        random.shuffle(values)
        for value in values:
            self.bst_tree.insert(Node(value))

    def main_loop(self):
        self.fps_sleeper()
        self.event_handler()
        if self.execute_input:
            thread = threading.Thread(target=self.input_handler)
            thread.start()
            self.execute_input = False
        self.renderer()
        self.recenter_view = False

    def event_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.lmb_down = True
            elif event.type == pygame.MOUSEBUTTONUP:
                self.lmb_down = False
            elif event.type == pygame.MOUSEMOTION:
                new_mpos = pygame.mouse.get_pos()
                if self.lmb_down and self.mouse_pos is not None:
                    self.view_scroll.x -= self.mouse_pos[0] - new_mpos[0]
                    self.view_scroll.y -= self.mouse_pos[1] - new_mpos[1]
                self.mouse_pos = new_mpos

            elif event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_MINUS
                        and self.node_radius - self.ZOOM_DELTA > 0
                        and self.depth_height_delta - self.ZOOM_DELTA * 3 > 0):
                    self.depth_height_delta -= self.ZOOM_DELTA * 3
                    self.node_radius -= self.ZOOM_DELTA
                    self.node_font = pygame.font.Font("Arvo-Bold.ttf", 16 * self.node_radius // 20)
                    self.input_mode = InputMode.NONE

                elif event.key == pygame.K_EQUALS:
                    self.depth_height_delta += self.ZOOM_DELTA * 3
                    self.node_radius += self.ZOOM_DELTA
                    self.node_font = pygame.font.Font("Arvo-Bold.ttf", 16 * self.node_radius // 20)
                    self.input_mode = InputMode.NONE

                elif event.key == pygame.K_i:
                    self.input_mode = InputMode.INSERT
                    self.input = ""
                elif event.key == pygame.K_d:
                    self.input_mode = InputMode.DELETE
                    self.input = ""
                elif event.key == pygame.K_s:
                    self.input_mode = InputMode.SEARCH
                    self.input = ""
                elif event.key == pygame.K_c:
                    if self.tree_view_mode == ViewMode.BST:
                        self.tree_view_mode = ViewMode.AVL
                    elif self.tree_view_mode == ViewMode.AVL:
                        self.tree_view_mode = ViewMode.BST
                    self.recenter_view = True

                elif event.key == pygame.K_1:
                    self.input += "1"
                elif event.key == pygame.K_2:
                    self.input += "2"
                elif event.key == pygame.K_3:
                    self.input += "3"
                elif event.key == pygame.K_4:
                    self.input += "4"
                elif event.key == pygame.K_5:
                    self.input += "5"
                elif event.key == pygame.K_6:
                    self.input += "6"
                elif event.key == pygame.K_7:
                    self.input += "7"
                elif event.key == pygame.K_8:
                    self.input += "8"
                elif event.key == pygame.K_9:
                    self.input += "9"
                elif event.key == pygame.K_0:
                    self.input += "0"

                elif event.key == pygame.K_RETURN:
                    self.execute_input = True

                elif event.key == pygame.K_UP:
                    self.tree_size += 3
                    self.initialize_trees()
                    self.input_mode = InputMode.INFO
                    self.input = "TREE SIZE = " + str(self.tree_size + 1)
                elif event.key == pygame.K_DOWN and self.tree_size - 3 >= 0:
                    self.tree_size -= 3
                    self.initialize_trees()
                    self.input_mode = InputMode.INFO
                    self.input = "TREE SIZE = " + str(self.tree_size + 1)
                elif event.key == pygame.K_LEFT:
                    self.bst_tree.anim_time = round(max(0.1, self.bst_tree.anim_time - 0.1), 1)
                    self.avl_tree.anim_time = round(max(0.1, self.avl_tree.anim_time - 0.1), 1)
                    self.input_mode = InputMode.INFO
                    self.input = "ANIM TIME = " + str(self.bst_tree.anim_time) + " s"
                elif event.key == pygame.K_RIGHT:
                    self.bst_tree.anim_time = round(min(2, self.bst_tree.anim_time + 0.1), 1)
                    self.avl_tree.anim_time = round(min(2, self.avl_tree.anim_time + 0.1), 1)
                    self.input_mode = InputMode.INFO
                    self.input = "ANIM TIME = " + str(self.bst_tree.anim_time) + " s"

                else:
                    self.input_mode = InputMode.NONE

    def renderer(self):
        self.screen.fill(self.BG_COLOR)
        self.render_help()
        self.render_input()
        self.render_tree()
        pygame.display.update()

    def fps_sleeper(self):
        self.timer.tick(self.FPS)

    def render_tree(self):
        self.node_count_per_depth_drawn = {}
        self.count_nodes_per_depth()

        if self.tree_view_mode == ViewMode.BST:
            self.x_node_span = max(self.bst_node_count_per_depth.values()) * self.node_radius * 3
        elif self.tree_view_mode == ViewMode.AVL:
            self.x_node_span = max(self.avl_node_count_per_depth.values()) * self.node_radius * 3
        else:
            self.x_node_span = self.RESOLUTION.x

        def calculate_point_recursive(node, parent_x, parent_y, min_x, max_x, y, parent_node):
            if node is None:
                return

            if node.depth not in self.node_count_per_depth_drawn:
                self.node_count_per_depth_drawn[node.depth] = 0.5

            if self.tree_view_mode == ViewMode.BST:
                x = self.x_node_span
                x *= self.node_count_per_depth_drawn[node.depth] / self.bst_node_count_per_depth[node.depth]

            elif self.tree_view_mode == ViewMode.AVL:
                x = self.x_node_span
                x *= self.node_count_per_depth_drawn[node.depth] / self.avl_node_count_per_depth[node.depth]
            else:
                x = -100

            x += self.view_scroll.x
            self.node_count_per_depth_drawn[node.depth] += 1

            if parent_node is not None:
                if parent_node.right is node:
                    pygame.draw.line(self.screen, self.LINE_COLOR_RIGHT, (x, y), (parent_x, parent_y), 2)
                if parent_node.left is node:
                    pygame.draw.line(self.screen, self.LINE_COLOR_LEFT, (x, y), (parent_x, parent_y), 2)

            calculate_point_recursive(node.right, x, y, x + self.node_radius, max_x, y + self.depth_height_delta, node)
            calculate_point_recursive(node.left, x, y, min_x, x - self.node_radius, y + self.depth_height_delta, node)

            mpos_dist = ((self.mouse_pos[0] - x) ** 2 + (self.mouse_pos[1] - y) ** 2)**0.5
            color = get_node_color(mpos_dist, node)

            pygame.draw.circle(self.screen, self.BG_COLOR, (x, y), self.node_radius)
            pygame.draw.circle(self.screen, color, (x, y), self.node_radius, 3)
            text = self.node_font.render(str(node.value), True, color)
            self.screen.blit(text, (x - text.get_width() // 2, y - text.get_height() // 2))
            if self.tree_view_mode == ViewMode.AVL:
                bal_text = self.help_font.render(str(self.avl_tree.calc_balance_factor(node)), True, color)
                self.screen.blit(bal_text, (x - bal_text.get_width() // 2 + self.node_radius, y - text.get_height() // 2 - self.node_radius))

        def get_node_color(mpos_dist, node):
            if ((self.tree_view_mode == ViewMode.BST and self.bst_tree.active_node is node) or
                    (self.tree_view_mode == ViewMode.AVL and mpos_dist <= self.node_radius * 1.5)):
                return self.HIGHLIGHTED_COLOR_BST
            elif (self.tree_view_mode == ViewMode.AVL and self.avl_tree.active_node is node or
                  (self.tree_view_mode == ViewMode.BST and mpos_dist <= self.node_radius * 1.5)):
                return self.HIGHLIGHTED_COLOR_AVL
            else:
                return pygame.color.Color(
                    max(0, self.NODE_COLOR_FULL.r - int(min(100, mpos_dist ** 2 / self.RESOLUTION.x))),
                    max(0, self.NODE_COLOR_FULL.g - int(min(100, mpos_dist ** 2 / self.RESOLUTION.x))),
                    max(0, self.NODE_COLOR_FULL.b - int(min(100, mpos_dist ** 2 / self.RESOLUTION.x)))
                )

        if self.recenter_view:
            self.center_view_scroll()
        self.node_points = []
        if self.tree_view_mode == ViewMode.BST:
            calculate_point_recursive(self.bst_tree.root, None, None, 0, self.RESOLUTION.x, 100 + self.view_scroll.y, None)
        if self.tree_view_mode == ViewMode.AVL:
            calculate_point_recursive(self.avl_tree.root, None, None, 0, self.RESOLUTION.x, 100 + self.view_scroll.y, None)

    def count_nodes_per_depth(self):
        self.bst_node_count_per_depth.clear()
        self.avl_node_count_per_depth.clear()

        def bst_add(node):
            if node.depth not in self.bst_node_count_per_depth:
                self.bst_node_count_per_depth[node.depth] = 0
            self.bst_node_count_per_depth[node.depth] += 1

        def avl_add(node):
            if node.depth not in self.avl_node_count_per_depth:
                self.avl_node_count_per_depth[node.depth] = 0
            self.avl_node_count_per_depth[node.depth] += 1

        self.bst_tree.traverse(bst_add)
        self.avl_tree.traverse(avl_add)

    def render_input(self):
        if self.input_mode == InputMode.NONE:
            self.input = self.tree_view_mode
        self.screen.blit(self.input_font.render(self.input_mode + " " + self.input, True, (200, 200, 200)), (20, 20))

    def input_handler(self):
        bst_visible = self.tree_view_mode == ViewMode.BST
        avl_visible = self.tree_view_mode == ViewMode.AVL
        if not self.input.isnumeric():
            return
        if self.input_mode == InputMode.INSERT:
            self.bst_tree.insert(Node(int(self.input)), bst_visible)
            self.avl_tree.insert(Node(int(self.input)), avl_visible)
        if self.input_mode == InputMode.DELETE:
            self.bst_tree.delete(self.bst_tree.search(int(self.input), bst_visible), bst_visible)
            self.avl_tree.delete(Node(int(self.input)), avl_visible)
        if self.input_mode == InputMode.SEARCH:
            self.bst_tree.search(int(self.input), bst_visible)
            self.avl_tree.search(int(self.input), avl_visible)
        self.count_nodes_per_depth()
        self.input_mode = InputMode.INFO
        self.input = ""

    def render_help(self):
        self.screen.blit(self.help_text, (10, self.RESOLUTION.y - 10 - self.help_text.get_height()))

    def center_view_scroll(self):
        self.view_scroll.y = 30
        self.view_scroll.x = self.RESOLUTION.x / 2 - self.x_node_span / 2


if __name__ == "__main__":
    App()
