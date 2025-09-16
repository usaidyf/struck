from textnode import TextNode, TextType
from htmlnode import LeafNode


def text_node_to_html_node(text_node):
    if text_node.text_type == TextType.PLAIN:
        return LeafNode(tag=None, value=text_node.text)
    if text_node.text_type == TextType.BOLD:
        return LeafNode(tag="b", value=text_node.text)
    if text_node.text_type == TextType.ITALIC:
        return LeafNode(tag="i", value=text_node.text)
    if text_node.text_type == TextType.CODE:
        return LeafNode(tag="code", value=text_node.text)
    if text_node.text_type == TextType.LINK:
        return LeafNode(tag="a", value=text_node.text, props={"href": text_node.url})
    if text_node.text_type == TextType.IMAGE:
        return LeafNode(
            tag="img", value=None, props={"src": text_node.url, "alt": text_node.text}
        )


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []

    for node in old_nodes:
        # Raise error if there's no closing delimiter
        if node.text.count(delimiter) % 2 != 0:
            raise ValueError(f"Unmatched delimiter '{delimiter}' in text: {node.text}")
        # Split only plain text nodes into alternating plain and formatted nodes
        if node.text_type != TextType.PLAIN:
            new_nodes.append(node)
            continue

        parts = node.text.split(delimiter)
        for i, part in enumerate(parts):
            if part == "":
                continue
            if i % 2 == 0:
                new_nodes.append(TextNode(part, TextType.PLAIN))
            else:
                new_nodes.append(TextNode(part, text_type))

    return new_nodes


def main():
    new_node = TextNode("This is some anchor text", "link", "https://example.com")
    print(new_node)


if __name__ == "__main__":
    main()
