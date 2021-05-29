from .common import *

import copy

class BasicTransformer:
    @staticmethod
    def transform (source: Source, comment_specifier: CommentSpecifier) -> Source:
        no_comments = BasicTransformer._remove_comments (source = source, comment_specifier = comment_specifier)
        no_empties = BasicTransformer._remove_empties (source = no_comments)
        return no_empties
    @staticmethod
    def _remove_comments (source: Source, comment_specifier: CommentSpecifier) -> Source:
        out_source = []
        for line in source:
            if line.startswith (comment_specifier): continue
            fixed_line = copy.deepcopy (line)
            if comment_specifier in fixed_line:
                fixed_line = comment_specifier.join (fixed_line.split (comment_specifier) [:-1]).rstrip ()
            out_source.append (fixed_line)
        return out_source
    @staticmethod
    def _remove_empties (source: Source) -> Source:
        out_source = []
        for line in source:
            if line.strip () == "": continue
            line_copy = copy.deepcopy (line)
            out_source.append (line_copy)
        return out_source