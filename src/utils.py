from htmlnode import LeafNode
from textnode import TextType, TextNode
import re


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


def extract_markdown_images(text):
    pattern = r"!\[([^\[\]]*)\]\(([^\(\)]*)\)"
    matches = re.findall(pattern, text)
    return matches


def extract_markdown_links(text):
    pattern = r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)"
    matches = re.findall(pattern, text)
    return matches


def split_nodes_image(old_nodes):
    new_nodes = []

    for node in old_nodes:
        if node.text_type != TextType.PLAIN:
            new_nodes.append(node)
            continue
        # Use the extract_markdown_images function to find images
        matches = extract_markdown_images(node.text)
        if not matches:
            new_nodes.append(node)
            continue
        last_index = 0
        for alt_text, url in matches:
            start_index = node.text.find(f"![{alt_text}]({url})", last_index)
            if start_index > last_index:
                new_nodes.append(
                    TextNode(node.text[last_index:start_index], TextType.PLAIN)
                )
            new_nodes.append(TextNode(alt_text, TextType.IMAGE, url))
            last_index = start_index + len(f"![{alt_text}]({url})")
        if last_index < len(node.text):
            new_nodes.append(TextNode(node.text[last_index:], TextType.PLAIN))

    return new_nodes


def split_nodes_link(old_nodes):
    new_nodes = []

    for node in old_nodes:
        if node.text_type != TextType.PLAIN:
            new_nodes.append(node)
            continue
        # Use the extract_markdown_links function to find links
        matches = extract_markdown_links(node.text)
        if not matches:
            new_nodes.append(node)
            continue
        last_index = 0
        for link_text, url in matches:
            start_index = node.text.find(f"[{link_text}]({url})", last_index)
            if start_index > last_index:
                new_nodes.append(
                    TextNode(node.text[last_index:start_index], TextType.PLAIN)
                )
            new_nodes.append(TextNode(link_text, TextType.LINK, url))
            last_index = start_index + len(f"[{link_text}]({url})")
        if last_index < len(node.text):
            new_nodes.append(TextNode(node.text[last_index:], TextType.PLAIN))

    return new_nodes
