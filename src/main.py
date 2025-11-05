import sys
from utils import copy_tree_clean, generate_pages_recursive


def main():
    base_path = sys.argv[1] if len(sys.argv) > 1 else "/"
    # Delete/clean and copy static assets into the generated docs directory
    copy_tree_clean("static", "docs")
    # Generate pages for all markdown files in the content directory
    generate_pages_recursive("content", "template.html", "docs", base_path)


if __name__ == "__main__":
    main()
