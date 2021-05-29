from .advanced_common import *
import re

Regex = str
MatchResult = Optional [re.Match]

class AdvancedTransformer:
    @staticmethod
    def transform (basic_list: BasicList) -> AppDefinition:
        app_definition: AppDefinition = AppDefinition ()

        for top_level_item in basic_list:
            print (f"item: {top_level_item}")
            matches, result = AdvancedTransformer._match (BasicStatementItem, top_level_item, r"instance (?P<name>.+) is (?P<type_name>.+)")
            if matches:
                print (f"matches! result is {result}, name is {result.group ('name')}, type_name is {result.group ('type_name')}")

        # TODO re-enable check once the advanced transformation can find and assign the main view
        # if app_definition.main_view is None: raise Exception ("No main view specified")

        return app_definition
    @staticmethod
    def _match (req_type: Union [type (BasicStatementItem), type (BasicBlockItem)], item: BasicItem, pattern: Regex) -> \
    tuple [bool, MatchResult]:
        if not isinstance (item, req_type): return False, None
        match_result = re.match (pattern, item.value)
        return match_result is not None, match_result