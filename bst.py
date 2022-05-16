from dataclasses import dataclass, field
from typing import TypeVar, Iterator

from PIL import Image

TreeNode = TypeVar("TreeNode")

FIRST_PIXELS = (1, 1)


@dataclass
class TreeNode:
    image: Image.Image
    left: TreeNode = None
    right: TreeNode = None


@dataclass
class Tree:
    sequence: Iterator[Image.Image]
    root: TreeNode = None

    def __post_init__(self):
        for image in self.sequence:
            self.insert(image, self.root)

    def insert(self, image: Image.Image, node: TreeNode = None) -> None:
        if not self.root:
            self.root = TreeNode(image)
        elif image.getpixel(FIRST_PIXELS) < node.image.getpixel(FIRST_PIXELS):
            if node.left is not None:
                self.insert(image, node.left)
            else:
                node.left = TreeNode(image)
        else:
            if node.right is not None:
                self.insert(image, node.right)
            else:
                node.right = TreeNode(image)

    def find(self, rgb: tuple[int, int, int], node: TreeNode = None) -> Image.Image:
        if not node:
            node = self.root

        node_pixels = node.image.getpixel(FIRST_PIXELS)

        if rgb < node_pixels:
            if node.left is not None:
                return self.find(rgb, node.left)
        elif rgb > node_pixels:
            if node.right is not None:
                return self.find(rgb, node.right)
        else:
            return node.image
