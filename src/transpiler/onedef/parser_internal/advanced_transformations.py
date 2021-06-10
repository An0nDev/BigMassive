from .advanced_common import *
from .advanced_utils import find_type, find_view, resolve_reference, match_basic_item, parse_view_definition_node
import re
from .advanced_regex_utils import Regex, NAMED, MatchResult

class AdvancedTransformer:
    @staticmethod
    def transform (basic_list: BasicList) -> AppDefinition:
        app_definition: AppDefinition = AppDefinition ()

        for top_level_item in basic_list:
            # print (f"item: {top_level_item}")

            is_type_definition_block, result = match_basic_item (BasicBlockItem, f"type {NAMED ('name')}", top_level_item)
            if is_type_definition_block:
                type_definition_block: BasicBlockItem = top_level_item
                _type: UserDefinedType = UserDefinedType (name = result.group ("name"))
                for type_definition_block_subitem in type_definition_block.subitems:
                    is_type_definition_fields_node, result = match_basic_item (BasicBlockItem, r"fields", type_definition_block_subitem)
                    if is_type_definition_fields_node:
                        type_definition_fields_node = type_definition_block_subitem
                        for type_definition_fields_node_subitem in type_definition_fields_node.subitems:
                            is_field_definition, result = match_basic_item (BasicStatementItem, f"{NAMED ('name')} is {NAMED ('type_name')}", type_definition_fields_node_subitem)
                            if is_field_definition:
                                field = Field (name = result.group ('name'), type = find_type (result.group ('type_name'), app_definition))
                                _type.fields.append (field)
                                continue

                            raise_out_of_context (type_definition_block_subitem, "type definition fields node")
                        continue

                    is_type_definition_actions_node, result = match_basic_item (BasicBlockItem, r"actions", type_definition_block_subitem)
                    if is_type_definition_actions_node:
                        type_definition_actions_node = type_definition_block_subitem
                        for type_definition_actions_node_subitem in type_definition_actions_node.subitems:
                            is_type_definition_action_node, result = match_basic_item (BasicBlockItem, NAMED ("name"), type_definition_actions_node_subitem)
                            if is_type_definition_action_node:
                                action = UserDefinedAction (name = result.group ("name"))
                                type_definition_action_node = type_definition_actions_node_subitem
                                for action_definition_node_item in type_definition_action_node.subitems:
                                    # TODO improve action definition node parsing to work generically/recursively
                                    is_pass_statement, result = match_basic_item (BasicStatementItem, "pass", action_definition_node_item)
                                    if is_pass_statement: continue

                                    is_assignment_statement, result = match_basic_item (BasicStatementItem, f"{NAMED ('lhs')} = {NAMED ('rhs')}", action_definition_node_item)
                                    if is_assignment_statement:
                                        action_definition_node = ActionDefinitionNode (
                                            type = ActionDefinitionNode.Type.ASSIGNMENT_STMT,
                                            extra = AssignmentStatementExtra (
                                                lhs = resolve_reference (result.group ("lhs")),
                                                rhs = resolve_reference (result.group ("rhs"))
                                            )
                                        )
                                        action.definition_nodes.append (action_definition_node)
                                        continue

                                    raise_out_of_context (action_definition_node_item, "type definition action node")
                                _type.actions.append (action)
                                continue

                            raise_out_of_context (type_definition_actions_node_subitem, "type definition actions node")
                        continue

                    raise_out_of_context (type_definition_block_subitem, "type definition")
                # TODO construction + population of field object
                app_definition.types.append (_type)
                continue

            is_instance_definition, result = match_basic_item (BasicStatementItem, f"instance {NAMED ('name')} is {NAMED ('type_name')}", top_level_item)
            if is_instance_definition:
                instance_definition: BasicStatementItem = top_level_item
                instance = CompileTimeInstance (name = result.group ("name"), type = find_type (result.group ("type_name"), app_definition))
                app_definition.instances.append (instance)
                continue

            is_view_definition, result = match_basic_item (BasicBlockItem, f"view {NAMED ('name')}", top_level_item)
            if is_view_definition:
                view_definition = top_level_item
                view = View (name = result.group ("name"))

                for view_definition_node_item in view_definition.subitems:
                    view_definition_node = parse_view_definition_node (source_item = view_definition_node_item, parent = None, app_definition = app_definition)
                    print ()
                    view.definition_nodes.append (view_definition_node)
                app_definition.views.append (view)
                continue

            is_main_view_definition, result = match_basic_item (BasicStatementItem, f"main view {NAMED ('name')}", top_level_item)
            if is_main_view_definition:
                app_definition.main_view = find_view (result.group ("name"), app_definition)
                continue

            raise_out_of_context (top_level_item, "top level")
        # TODO re-enable check once the advanced transformation can find and assign the main view
        if app_definition.main_view is None: raise Exception ("No main view specified")

        return app_definition
