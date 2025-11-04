class HTMLNode:
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError("Subclasses must implement to_html method")

    def props_to_html(self):
        if not self.props:
            return ""
        props_str = " ".join(f'{key}="{value}"' for key, value in self.props.items())
        return f" {props_str}"


class LeafNode(HTMLNode):
    def __init__(self, tag, value, props=None):
        super().__init__(tag=tag, value=value, props=props)

    def to_html(self):
        # Support void/self-closing tags (e.g., img, br, hr, input, meta, link)
        void_tags = {
            "img",
            "br",
            "hr",
            "input",
            "meta",
            "link",
            "source",
            "track",
            "area",
            "base",
            "col",
            "embed",
            "param",
            "wbr",
        }
        if self.tag is None:
            return self.value
        if self.tag in void_tags:
            # Render as self-closing; ignore value
            return f"<{self.tag}{self.props_to_html()} />"
        if self.value is None:
            raise ValueError("LeafNode must have a value")

        return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"


class ParentNode(HTMLNode):
    def __init__(self, tag, children, props=None):
        super().__init__(tag=tag, children=children, props=props)

    def to_html(self):
        if self.tag is None:
            raise ValueError("ParentNode must have a tag")
        if self.children is None:
            raise ValueError("ParentNode must have children")

        children_html = "".join(child.to_html() for child in self.children)
        return f"<{self.tag}{self.props_to_html()}>{children_html}</{self.tag}>"
