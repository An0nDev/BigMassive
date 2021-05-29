from .common import *
import copy

class IndentReader:
    @staticmethod
    def read (source: Source, indent_specifier: IndentSpecifier) -> SourceWithIndentCount:
        source_with_indent_count = []
        for line in source:
            copied_line = copy.deepcopy (line)
            indent_count = 0
            while copied_line.startswith (indent_specifier):
                copied_line = copied_line [len (indent_specifier):]
                indent_count += 1
            line_with_indent_count = LineWithIndentCount (line = copied_line, indent_count = indent_count)
            source_with_indent_count.append (line_with_indent_count)
        return source_with_indent_count