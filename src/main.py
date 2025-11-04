from utils import copy_tree_clean, generate_page


def main():
    # Delete/clean and copy static assets into the generated public directory
    copy_tree_clean("static", "public")
    # Generate the main page from markdown using the HTML template
    generate_page("content/index.md", "template.html", "public/index.html")


if __name__ == "__main__":
    main()
