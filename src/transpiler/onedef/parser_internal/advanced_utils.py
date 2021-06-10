from .advanced_native_types import *
import re
from .advanced_regex_utils import NAMED, Regex, MatchResult

class BaseNamedException (Exception):
    def __init__ (self, *args, _name: Name):
        super ().__init__ (*args)
        self._name = _name

class UnknownException (BaseNamedException): pass
class MultipleDefinitionException (BaseNamedException): pass
class InstantiatingNonGenericException (BaseNamedException): pass

def find_type (type_name: Name, app_definition: AppDefinition):
    generic_result = re.match (f"{NAMED ('generic_name')} of {NAMED ('target_name')}", type_name)
    if generic_result is not None: # is generic
        generic_type_name = generic_result.group ("generic_name")
        generic_type = find_type (generic_type_name, app_definition = app_definition)
        if not isinstance (generic_type, GenericType):
            raise InstantiatingNonGenericException (f"Instantiating non-generic type {generic_type_name}", _name = generic_type_name)
        target_type = find_type (generic_result.group ("target_name"), app_definition = app_definition)
        return GenericInstantiation (
            generic_type = generic_type,
            target_type = target_type
        )
    return _basic_find_thing_single (kind_of_thing = "type", target = type_name, container = app_definition.types + Builtins)

def find_view (view_name: Name, app_definition: AppDefinition):
    return _basic_find_thing_single (kind_of_thing = "view", target = view_name, container = app_definition.views)

def _basic_find_thing_single (kind_of_thing: str, target: str, container: List):
    matches = [thing for thing in container if thing.name == target]
    if len (matches) == 0: raise UnknownException (f"Unknown {kind_of_thing} {target}", _name = target)
    if len (matches) > 1: raise MultipleDefinitionException (f"Multiple definitions of {kind_of_thing} {target}", _name = target)
    return matches [0]

def match_basic_item (_type: Union [type (BasicStatementItem), type (BasicBlockItem)], pattern: Regex, item: BasicItem) -> \
tuple [bool, MatchResult]:
    if not isinstance (item, _type): return False, None
    match_result = re.fullmatch (pattern, item.value)
    return match_result is not None, match_result

def resolve_constant (source: str, match_unqualified_strings: bool = False) -> Optional [Constant]:
    string_match = re.fullmatch (f"\"{NAMED ('value')}\"", source)
    if string_match is not None: return Constant (type = Builtins [0], native_value = string_match.group ("value"))
    boolean_match = re.fullmatch ("(True)|(False)", source)
    if boolean_match is not None: return Constant (type = Builtins [1], native_value = source == "True")
    if match_unqualified_strings: return Constant (type = Builtins [0], native_value = source)
    return None

def resolve_reference (source: str):
    # constants
    constant = resolve_constant (source)
    if constant is not None: return constant

    field_match = re.fullmatch (f"{NAMED ('parent')}\.{NAMED ('field')}", source)
    if field_match is not None:
        return FieldReference (name = field_match.group ("field"), parent = LocalReference (name = field_match.group ("parent")))

    return LocalReference (name = source)

def add_reference_to_view_definition_node_tree (lowest_node: ViewDefinitionNode, reference: Reference):
    next_node = lowest_node
    while next_node is not None:
        if reference in next_node.generates: return
        next_node.references.append (reference)
        next_node = next_node.parent

def parse_view_definition_node (source_item: BasicItem, parent: Optional [ViewDefinitionNode], app_definition: AppDefinition) -> ViewDefinitionNode:
    is_foreach_block, result = match_basic_item (BasicBlockItem, f"foreach {NAMED ('new_name')} in {NAMED ('source')}", source_item)
    if is_foreach_block:
        source = resolve_reference (result.group ("source"))
        foreach_block_node = ViewDefinitionNode (type = ViewDefinitionNode.Type.FOREACH_BLOCK, extra = ForeachBlockExtra (
            new_name = result.group ("new_name"),
            source = source
        ), generates = [LocalReference (name = result.group ("new_name"))], references = [source], parent = parent)
        add_reference_to_view_definition_node_tree (lowest_node = parent, reference = source)
        for subitem in source_item.subitems:
            foreach_block_node.subnodes.append (parse_view_definition_node (source_item = subitem, parent = foreach_block_node, app_definition = app_definition))
        return foreach_block_node

    is_form_definition_block, result = match_basic_item (BasicBlockItem, f"form for {NAMED ('action')} {NAMED ('target')}", source_item)
    if is_form_definition_block:
        raise NotImplementedError ()

    is_node_definition_block, result = match_basic_item (BasicBlockItem, f"node {NAMED ('name')}", source_item)
    if is_node_definition_block:
        node_definition_block_node = ViewDefinitionNode (type = ViewDefinitionNode.Type.NODE_DEFINITION_BLOCK, extra = NodeDefinitionExtra (

        ), parent = parent)
        for subitem in source_item.subitems:
            subnode = parse_view_definition_node (source_item = subitem, parent = node_definition_block_node, app_definition = app_definition)

    raise_out_of_context (source_item, "view definition")