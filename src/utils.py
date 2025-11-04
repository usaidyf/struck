from htmlnode import LeafNode, ParentNode
from textnode import TextType, TextNode
from blocknode import BlockType, block_to_block_type
import re
import textwrap
import os
import shutil


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


def text_to_textnodes(text):
    nodes = [TextNode(text, TextType.PLAIN)]
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    return nodes


def markdown_to_blocks(markdown):
    return [y for y in ([x.strip() for x in markdown.split("\n\n")]) if y != ""]


def markdown_to_html_node(markdown):
    # Helper to convert inline markdown text into HTMLNode children
    def text_to_children(text):
        return [text_node_to_html_node(n) for n in text_to_textnodes(text)]

    # Helper to process heading blocks
    def heading_block_to_node(block):
        first_line = block.splitlines()[0].strip()
        level = len(first_line) - len(first_line.lstrip("#"))
        level = min(max(level, 1), 6)
        text = first_line[level:].strip()
        return ParentNode(f"h{level}", text_to_children(text))

    # Helper to process paragraph blocks (merge lines with spaces)
    def paragraph_block_to_node(block):
        text = (
            " ".join(
                [line.strip() for line in block.splitlines() if line.strip() != ""]
            )
            if "\n" in block
            else block.strip()
        )
        return ParentNode("p", text_to_children(text))

    # Helper to process blockquote blocks (strip leading ">" per line)
    def quote_block_to_node(block):
        lines = []
        for line in block.splitlines():
            # Remove leading '>' and optional space
            stripped = re.sub(r"^>\s?", "", line.strip())
            if stripped != "":
                lines.append(stripped)
        text = " ".join(lines)
        return ParentNode("blockquote", text_to_children(text))

    # Helper to process unordered list blocks
    def ul_block_to_node(block):
        items = []
        for line in block.splitlines():
            s = line.strip()
            if not s:
                continue
            if s.startswith("- "):
                item_text = s[2:].strip()
                items.append(ParentNode("li", text_to_children(item_text)))
        return ParentNode("ul", items)

    # Helper to process ordered list blocks
    def ol_block_to_node(block):
        items = []
        for line in block.splitlines():
            s = line.strip()
            if not s:
                continue
            m = re.match(r"^(\d+)\.\s+(.*)$", s)
            if m:
                item_text = m.group(2).strip()
                items.append(ParentNode("li", text_to_children(item_text)))
        return ParentNode("ol", items)

    # Helper to process code blocks (no inline parsing)
    def code_block_to_node(block):
        # Normalize block and remove opening/closing fences
        content = block.strip()
        lines = content.split("\n")
        # Remove opening fence line
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        # Remove closing fence line
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        # Dedent common leading whitespace introduced by triple-quoted formatting
        code_body = "\n".join(lines)
        code_body = textwrap.dedent(code_body)
        # Ensure trailing newline as per expected output
        if not code_body.endswith("\n"):
            code_body += "\n"
        return ParentNode("pre", [LeafNode("code", code_body)])

    blocks = markdown_to_blocks(markdown)
    children = []
    for block in blocks:
        btype = block_to_block_type(block)
        if btype == BlockType.HEADING:
            children.append(heading_block_to_node(block))
        elif btype == BlockType.QUOTE:
            children.append(quote_block_to_node(block))
        elif btype == BlockType.UNORDERED_LIST:
            children.append(ul_block_to_node(block))
        elif btype == BlockType.ORDERED_LIST:
            children.append(ol_block_to_node(block))
        elif btype == BlockType.CODE:
            children.append(code_block_to_node(block))
        else:
            children.append(paragraph_block_to_node(block))

    return ParentNode("div", children)


def _copy_dir_contents(src_dir, dst_dir):
    """Recursively copy contents of src_dir into dst_dir.

    Assumes dst_dir already exists. Logs each file copied.
    """
    for entry in os.listdir(src_dir):
        src_path = os.path.join(src_dir, entry)
        dst_path = os.path.join(dst_dir, entry)
        if os.path.isdir(src_path):
            os.makedirs(dst_path, exist_ok=True)
            _copy_dir_contents(src_path, dst_path)
        else:
            # Copy file and preserve metadata
            shutil.copy2(src_path, dst_path)
            print(f"Copied {src_path} -> {dst_path}")


def copy_tree_clean(src_dir, dst_dir):
    """Delete dst_dir (if exists) and copy entire src_dir tree into it.

    - Removes the destination directory to ensure a clean copy
    - Recursively copies files and subdirectories
    - Logs each copied file path
    """
    if not os.path.exists(src_dir):
        raise FileNotFoundError(f"Source directory does not exist: {src_dir}")

    if os.path.exists(dst_dir):
        shutil.rmtree(dst_dir)
    os.makedirs(dst_dir, exist_ok=True)

    _copy_dir_contents(src_dir, dst_dir)


def extract_title(markdown):
    """Extract the H1 title (line starting with a single '# ') from markdown.

    Returns the stripped title text. Raises a ValueError if no H1 exists.
    Leading whitespace on each line is ignored, so indented H1s are supported.
    """
    for line in markdown.splitlines():
        s = line.strip()
        if s.startswith("# "):
            return s[2:].strip()
    raise ValueError("No H1 title ('# ') found in markdown")


def generate_page(from_path, template_path, dest_path):
    """Generate a full HTML page from a markdown file and an HTML template.

    - Logs the operation
    - Converts markdown to HTML using markdown_to_html_node().to_html()
    - Extracts title using extract_title()
    - Replaces {{ Title }} and {{ Content }} in the template
    - Writes output to dest_path, creating directories as needed
    """
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")

    with open(from_path, "r", encoding="utf-8") as f:
        md = f.read()
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    html_node = markdown_to_html_node(md)
    content_html = html_node.to_html()
    title = extract_title(md)

    full_html = template.replace("{{ Title }}", title).replace(
        "{{ Content }}", content_html
    )

    dest_dir = os.path.dirname(dest_path)
    if dest_dir:
        os.makedirs(dest_dir, exist_ok=True)
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(full_html)
