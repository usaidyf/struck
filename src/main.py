from textnode import TextNode
from utils import copy_tree_clean


def main():
    # Copy all static assets into the generated public directory
    copy_tree_clean("static", "public")

    # Existing demo output (harmless for tests/manual run)
    new_node = TextNode("This is some anchor text", "link", "https://example.com")
    print(new_node)


if __name__ == "__main__":
    main()
