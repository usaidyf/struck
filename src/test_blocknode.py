import unittest
from blocknode import block_to_block_type, BlockType


class TestBlockNode(unittest.TestCase):
    def test_block_to_block_type(self):
        self.assertEqual(block_to_block_type("# Heading 1"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("## Heading 2"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("### Heading 3"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("#### Heading 4"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("##### Heading 5"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("###### Heading 6"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("> This is a quote"), BlockType.QUOTE)
        self.assertEqual(block_to_block_type(">This is also a quote"), BlockType.QUOTE)
        self.assertEqual(block_to_block_type("1. First item"), BlockType.ORDERED_LIST)
        self.assertEqual(block_to_block_type("22. Twenty second item"), BlockType.ORDERED_LIST)
        self.assertEqual(
            block_to_block_type("- Unordered item"), BlockType.UNORDERED_LIST
        )
        self.assertEqual(
            block_to_block_type("```python\nprint('Hello, World!')\n```"),
            BlockType.CODE,
        )
        self.assertEqual(
            block_to_block_type("This is a regular paragraph."), BlockType.PARAGRAPH
        )
        self.assertEqual(
            block_to_block_type("This is a paragraph with **bold** text."),
            BlockType.PARAGRAPH,
        )