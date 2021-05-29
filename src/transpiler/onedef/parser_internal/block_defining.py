import copy

from .common import *

class BlockDefiner:
    @staticmethod
    def define (source_with_indent_count: SourceWithIndentCount, block_specifier: BlockSpecifier) -> BasicList:
        stack: BasicList = []
        top_levels: BasicList = []
        for line_with_indent_count in source_with_indent_count:
            indent_count = line_with_indent_count.indent_count
            if indent_count > len (stack): raise Exception ("unexpected indent")
            while indent_count < len (stack): stack.pop (-1)
            is_block = line_with_indent_count.line.endswith (block_specifier)
            line_copy = copy.deepcopy (line_with_indent_count.line)
            value = line_copy [:-len (block_specifier)] if is_block else line_copy
            parent = stack [-1] if len (stack) > 0 else None
            item = BasicBlockItem (value = value, parent = parent) if is_block else BasicStatementItem (value = value, parent = parent)
            if parent is not None:
                parent.subitems.append (item)
            else:
                top_levels.append (item)
            if is_block:
                stack.append (item)
        return top_levels