from utils import copy_tree_clean, generate_pages_recursive


def main():
    # Delete/clean and copy static assets into the generated public directory
    copy_tree_clean("static", "public")
    # Generate pages for all markdown files in the content directory
    generate_pages_recursive("content", "template.html", "public")


if __name__ == "__main__":
    main()
