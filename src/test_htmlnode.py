import unittest
from htmlnode import HTMLNode


class TestHTMLNode(unittest.TestCase):
    def test_init(self):
        node = HTMLNode("div", "Hello", [], {"class": "container"})
        self.assertEqual(node.tag, "div")
        self.assertEqual(node.value, "Hello")
        self.assertEqual(node.children, [])
        self.assertEqual(node.props, {"class": "container"})

    def test_props_to_html(self):
        node = HTMLNode("div", "Hello", [], {"class": "container", "id": "main"})
        props_html = node.props_to_html()
        self.assertIn('class="container"', props_html)
        self.assertIn('id="main"', props_html)
        self.assertTrue(props_html.startswith(" "))

    def test_to_html_not_implemented(self):
        node = HTMLNode("div", "Hello")
        with self.assertRaises(NotImplementedError):
            node.to_html()


if __name__ == "__main__":
    unittest.main()
