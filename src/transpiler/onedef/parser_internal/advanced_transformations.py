from .advanced_common import *
import re

Regex = str
def NAMED (name: str, matcher: Regex = ".+") -> Regex: return f"(?P<{name}>{matcher})" # generates named match group regex component, with matcher being regex specifier for contents
MatchResult = Optional [re.Match]

class AdvancedTransformer:
    @staticmethod
    def transform (basic_list: BasicList) -> AppDefinition:
        app_definition: AppDefinition = AppDefinition ()
        def raise_out_of_context (_subitem: BasicItem, block_type: str): raise Exception (f"subitem {_subitem} seems to be out of context in a {block_type} block")

        for top_level_item in basic_list:
            # print (f"item: {top_level_item}")

            is_type_definition_block, result = AdvancedTransformer._match (BasicBlockItem, f"type {NAMED ('name')}", top_level_item)
            if is_type_definition_block:
                type_definition_block: BasicBlockItem = top_level_item
                _type: UserDefinedType = UserDefinedType (name = result.group ("name"))
                for type_definition_block_subitem in type_definition_block.subitems:
                    is_type_definition_fields_node, result = AdvancedTransformer._match (BasicBlockItem, r"fields", type_definition_block_subitem)
                    if is_type_definition_fields_node:
                        type_definition_fields_node = type_definition_block_subitem
                        for type_definition_fields_node_subitem in type_definition_fields_node.subitems:
                            is_field_definition, result = AdvancedTransformer._match (BasicStatementItem, f"{NAMED ('name')} is {NAMED ('type')}", type_definition_fields_node_subitem)
                            if is_field_definition:
                                field_definition = type_definition_fields_node_subitem
                                print (f"TODO parse field definition with name {result.group ('name')} and type {result.group ('type')}")  # TODO more parsing of field definition
                                # _type.fields.append ()
                                continue

                            raise_out_of_context (type_definition_block_subitem, "type definition fields node")
                        continue

                    is_type_definition_actions_node, result = AdvancedTransformer._match (BasicBlockItem, r"actions", type_definition_block_subitem)
                    if is_type_definition_actions_node:
                        type_definition_actions_node = type_definition_block_subitem
                        for type_definition_actions_node_subitem in type_definition_actions_node.subitems:
                            is_type_definition_action_node, result = AdvancedTransformer._match (BasicBlockItem, r"(?P<name>.+)", type_definition_actions_node_subitem)
                            if is_type_definition_action_node:
                                type_definition_action_node = type_definition_actions_node_subitem
                                print (f"TODO parse action node: {type_definition_action_node}") # TODO more parsing of action node
                                continue

                            raise_out_of_context (type_definition_actions_node_subitem, "type definition actions node")
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