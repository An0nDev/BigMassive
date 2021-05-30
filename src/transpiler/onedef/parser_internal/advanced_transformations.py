from .advanced_common import *
import re

Regex = str
MatchResult = Optional [re.Match]

class AdvancedTransformer:
    @staticmethod
    def transform (basic_list: BasicList) -> AppDefinition:
        app_definition: AppDefinition = AppDefinition ()
        def raise_out_of_context (_subitem: BasicItem, block_type: str): raise Exception (f"subitem {_subitem} seems to be out of context in a {block_type} block")

        for top_level_item in basic_list:
            print (f"item: {top_level_item}")

            is_type_definition_block, result = AdvancedTransformer._match (BasicBlockItem, r"type (?P<name>.+)", top_level_item)
            if is_type_definition_block:
                type_definition_block: BasicBlockItem = top_level_item
                for type_definition_block_subitem in type_definition_block.subitems:
                    is_type_definition_fields_node, result = AdvancedTransformer._match (BasicBlockItem, r"fields", type_definition_block_subitem)
                    if is_type_definition_fields_node:
                        type_definition_fields_node = type_definition_block_subitem
                        for field_definition in type_definition_fields_node.subitems:
                            print (f"field definition: {field_definition}")
                            # TODO more parsing of field definition
                        continue

                    is_type_definition_actions_node, result = AdvancedTransformer._match (BasicBlockItem, r"actions", type_definition_block_subitem)
                    if is_type_definition_actions_node:
                        type_definition_actions_node = type_definition_block_subitem
                        for action_definition_block in type_definition_actions_node.subitems:
                            print (f"action definition: {action_definition_block}")
                            # TODO more parsing of action definition
                        continue

                    raise_out_of_context (type_definition_block_subitem, "type definition")
                # TODO construction + population of field object
                continue

            is_instance_definition, result = AdvancedTransformer._match (BasicStatementItem, r"instance (?P<name>.+) is (?P<type_name>.+)", top_level_item)
            if is_instance_definition:
                instance_definition: BasicStatementItem = top_level_item
                print (f"instance definition: {instance_definition}")
                # TODO more parsing of instance definition
                continue

            raise_out_of_context (top_level_item, "top level")
        # TODO re-enable check once the advanced transformation can find and assign the main view
        # if app_definition.main_view is None: raise Exception ("No main view specified")

        return app_definition
    @staticmethod
    def _match (_type: Union [type (BasicStatementItem), type (BasicBlockItem)], pattern: Regex, item: BasicItem) -> \
    tuple [bool, MatchResult]:
        if not isinstance (item, _type): return False, None
        match_result = re.match (pattern, item.value)
        return match_result is not None, match_result