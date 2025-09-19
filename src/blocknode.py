from enum import Enum
import re


class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"

def block_to_block_type(markdown):
    heading_types = ["# ", "## ", "### ", "#### ", "##### ", "###### "]
    num_and_dot_re = r"^\d+\.\ "
    
    if any([markdown.startswith(ht) for ht in heading_types]):
        return BlockType.HEADING
    elif markdown.startswith(">"):
        return BlockType.QUOTE
    elif re.match(num_and_dot_re, markdown):
        return BlockType.ORDERED_LIST
    elif markdown.startswith("- "):
        return BlockType.UNORDERED_LIST
    elif markdown.startswith("```") and markdown.endswith("```"):
        return BlockType.CODE
    else:
        return BlockType.PARAGRAPH