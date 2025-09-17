import unittest

from textnode import TextNode, TextType
from utils import (
    extract_markdown_images,
    extract_markdown_links,
    split_nodes_image,
    split_nodes_link,
    text_node_to_html_node,
    split_nodes_delimiter,
)


class TestMain(unittest.TestCase):
    def test_text(self):
        node = TextNode("This is a text node", TextType.PLAIN)
        node2 = TextNode("This is a bold text node", TextType.BOLD)

        html_node = text_node_to_html_node(node)
        html_node2 = text_node_to_html_node(node2)

        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")
        self.assertEqual(html_node2.tag, "b")
        self.assertEqual(html_node2.value, "This is a bold text node")

    def test_link(self):
        node = TextNode("This is a link", TextType.LINK, "https://example.com")
        html_node = text_node_to_html_node(node)

        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "This is a link")
        self.assertEqual(html_node.props, {"href": "https://example.com"})

    def test_image(self):
        node = TextNode(
            "This is an image", TextType.IMAGE, "https://example.com/image.png"
        )
        html_node = text_node_to_html_node(node)

        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, None)
        self.assertEqual(
            html_node.props,
            {"src": "https://example.com/image.png", "alt": "This is an image"},
        )

    def test_unmatched_delimiter(self):

        nodes = [
            TextNode("This is *bold text without closing delimiter", TextType.PLAIN)
        ]
        delimiter = "*"
        text_type = TextType.BOLD

        with self.assertRaises(ValueError) as context:
            split_nodes_delimiter(nodes, delimiter, text_type)

        self.assertIn("Unmatched delimiter", str(context.exception))

    def test_split_nodes_delimiter(self):
        nodes = [
            TextNode(
                "This is **bold** text with **multiple** delimiters", TextType.PLAIN
            )
        ]
        delimiter = "**"
        text_type = TextType.BOLD

        new_nodes = split_nodes_delimiter(nodes, delimiter, text_type)

        self.assertEqual(len(new_nodes), 5)
        self.assertEqual(new_nodes[0].text, "This is ")
        self.assertEqual(new_nodes[0].text_type, TextType.PLAIN)
        self.assertEqual(new_nodes[1].text, "bold")
        self.assertEqual(new_nodes[1].text_type, TextType.BOLD)
        self.assertEqual(new_nodes[2].text, " text with ")
        self.assertEqual(new_nodes[3].text, "multiple")
        self.assertEqual(new_nodes[3].text_type, TextType.BOLD)
        self.assertEqual(new_nodes[4].text, " delimiters")
        self.assertEqual(new_nodes[4].text_type, TextType.PLAIN)

        nodes = [
            TextNode("This is _italic_ text with _multiple_ delimiters", TextType.PLAIN)
        ]
        delimiter = "_"
        text_type = TextType.ITALIC

        new_nodes = split_nodes_delimiter(nodes, delimiter, text_type)

        self.assertEqual(len(new_nodes), 5)
        self.assertEqual(new_nodes[0].text, "This is ")
        self.assertEqual(new_nodes[1].text, "italic")
        self.assertEqual(new_nodes[1].text_type, TextType.ITALIC)
        self.assertEqual(new_nodes[2].text, " text with ")
        self.assertEqual(new_nodes[3].text, "multiple")
        self.assertEqual(new_nodes[3].text_type, TextType.ITALIC)
        self.assertEqual(new_nodes[4].text, " delimiters")

    def test_split_nodes_delimiter_advanced(self):
        nodes = [
            TextNode(
                "This is **bold** text and _italic_ text with `code`", TextType.PLAIN
            )
        ]
        delimiter = "**"
        text_type = TextType.BOLD

        new_nodes = split_nodes_delimiter(nodes, delimiter, text_type)
        self.assertEqual(len(new_nodes), 3)
        self.assertEqual(new_nodes[0].text, "This is ")
        self.assertEqual(new_nodes[1].text, "bold")
        self.assertEqual(new_nodes[2].text, " text and _italic_ text with `code`")

        nodes = [
            TextNode("This is _italic_", TextType.PLAIN),
            TextNode(" and this is **bold**", TextType.PLAIN),
            TextNode(" and this is `code`", TextType.PLAIN),
        ]
        delimiter = "`"
        text_type = TextType.CODE

        new_nodes = split_nodes_delimiter(nodes, delimiter, text_type)
        self.assertEqual(len(new_nodes), 4)
        self.assertEqual(new_nodes[0].text, "This is _italic_")
        self.assertEqual(new_nodes[0].text_type, TextType.PLAIN)
        self.assertEqual(new_nodes[1].text, " and this is **bold**")
        self.assertEqual(new_nodes[1].text_type, TextType.PLAIN)
        self.assertEqual(new_nodes[2].text, " and this is ")
        self.assertEqual(new_nodes[3].text, "code")
        self.assertEqual(new_nodes[3].text_type, TextType.CODE)

        new_nodes = split_nodes_delimiter(new_nodes, "_", TextType.ITALIC)
        self.assertEqual(len(new_nodes), 5)
        self.assertEqual(new_nodes[0].text, "This is ")
        self.assertEqual(new_nodes[1].text, "italic")
        self.assertEqual(new_nodes[1].text_type, TextType.ITALIC)

        new_nodes = split_nodes_delimiter(new_nodes, "**", TextType.BOLD)
        self.assertEqual(len(new_nodes), 6)
        self.assertEqual(new_nodes[2].text, " and this is ")
        self.assertEqual(new_nodes[3].text, "bold")
        self.assertEqual(new_nodes[3].text_type, TextType.BOLD)
        self.assertEqual(new_nodes[4].text, " and this is ")
        self.assertEqual(new_nodes[5].text, "code")
        self.assertEqual(new_nodes[5].text_type, TextType.CODE)

    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_markdown_links(self):
        matches = extract_markdown_links(
            "This is a link to [example](https://example.com)"
        )
        self.assertListEqual([("example", "https://example.com")], matches)

    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.PLAIN,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.PLAIN),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.PLAIN),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )
        node = TextNode(
            "This is a text without images or links", TextType.PLAIN
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual([node], new_nodes)
        node = TextNode(
            "This is some text which shouldn't be converted",
            TextType.BOLD,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual([node], new_nodes)

    def test_split_links(self):
        node = TextNode(
            "This is a link to [example](https://example.com) and another [second link](https://example.org)",
            TextType.PLAIN,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is a link to ", TextType.PLAIN),
                TextNode("example", TextType.LINK, "https://example.com"),
                TextNode(" and another ", TextType.PLAIN),
                TextNode("second link", TextType.LINK, "https://example.org"),
            ],
            new_nodes,
        )
        node = TextNode(
            "This is a text without links or images", TextType.PLAIN
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual([node], new_nodes)
        node = TextNode(
            "This is some text which shouldn't be converted",
            TextType.BOLD,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual([node], new_nodes)

if __name__ == "__main__":
    unittest.main()
