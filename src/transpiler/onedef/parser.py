from .parser_internal.common import *
from .parser_internal.basic_transformations import BasicTransformer
from .parser_internal.indent_reading import IndentReader
from .parser_internal.block_defining import BlockDefiner
from .parser_internal.advanced_transformations import AdvancedTransformer
from .parser_internal.advanced_common import AppDefinition

@dataclasses.dataclass
class Config:
    comment_specifier: CommentSpecifier = "#"
    indent_specifier: IndentSpecifier = "    "
    block_specifier: BlockSpecifier = ":"

class Parser:
    @staticmethod
    def parse (source: Source, config: Config = Config ()) -> AppDefinition:
        post_basic_pass = BasicTransformer.transform (source = source, comment_specifier = config.comment_specifier)
        with_indent_count = IndentReader.read (source = post_basic_pass, indent_specifier = config.indent_specifier)
        basic_list = BlockDefiner.define (source_with_indent_count = with_indent_count, block_specifier = config.block_specifier)
        app_definition = AdvancedTransformer.transform (basic_list = basic_list)
        return app_definition