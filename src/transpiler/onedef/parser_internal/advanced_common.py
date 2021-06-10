from typing import Dict

from .common import *

import enum
import copy

Name = str

def _list (): return copy.deepcopy (dataclasses.field (default_factory = list))

@dataclasses.dataclass
class Field:
    name: Name
    type: "Type"

@dataclasses.dataclass
class LocalReference:
    name: Name

@dataclasses.dataclass
class FieldReference:
    name: Name
    parent: LocalReference

@dataclasses.dataclass
class Constant:
    type: "NativeType"
    native_value: Union [str, bool]

NonConstantReference = Union [LocalReference, FieldReference]
Reference = Union [LocalReference, FieldReference, Constant]

@dataclasses.dataclass
class AssignmentStatementExtra:
    lhs: NonConstantReference
    rhs: Reference

ActionDefinitionNodeExtra = Union [AssignmentStatementExtra]

@dataclasses.dataclass
class ActionDefinitionNode:
    class Type (enum.Enum):
        ASSIGNMENT_STMT = enum.auto
    type: Type
    extra: ActionDefinitionNodeExtra
    references: List ["Instance"] = dataclasses.field (default_factory = list) # NOT FILLED BY ADVANCED PASS YET

class Platform (enum.Enum):
    CLIENT_JS = enum.auto
    SERVER_PY = enum.auto

NativeImplementationLinePart = str
NativeImplementationLine = str
@dataclasses.dataclass
class SpecialNativeImplementationLine:
    class Type (enum.Enum):
        CALL_GENERIC_TARGET_CTOR = enum.auto # for a generic type, calls the constructor of the target type using the arguments passed to the action
        GET_NEXT_UNIQUE_ID = enum.auto # for lists, requests from the server a unique id for a new object in the list
    type: Type
    prefix: NativeImplementationLinePart = ""
    suffix: NativeImplementationLinePart = ""

NativeImplementation = List [Union [NativeImplementationLine, SpecialNativeImplementationLine]]
NativeImplementations = Dict [Platform, NativeImplementation]

Argument = Name

@dataclasses.dataclass
class Signature:
    is_static: bool
    arguments: Optional [List [Argument]] # if None, is not validated. notably used for List::add
    has_return_value: bool

@dataclasses.dataclass
class NativeAction:
    name: Name
    signature: Optional [Signature]
    native_implementations: NativeImplementations

@dataclasses.dataclass
class UserDefinedAction:
    name: Name
    definition_nodes: List [ActionDefinitionNode] = dataclasses.field (default_factory = list)

@dataclasses.dataclass
class NativeType:
    name: Name
    actions: List [NativeAction]

GenericType = NativeType

@dataclasses.dataclass
class GenericInstantiation:
    generic_type: GenericType
    target_type: "Type"

@dataclasses.dataclass
class UserDefinedType:
    name: Name
    fields: List [Field] = dataclasses.field (default_factory = list)
    actions: List [UserDefinedAction] = dataclasses.field (default_factory = list)

Type = Union [NativeType, UserDefinedType]

@dataclasses.dataclass
class CompileTimeInstance:
    name: Name
    type: Type
    # fields: List ["Instance"]
    # parent: Optional ["Instance"]

@dataclasses.dataclass
class RuntimeInstance:
    name: Name
    type: Type
    value: Optional [CompileTimeInstance]

Instance = Union [CompileTimeInstance, RuntimeInstance]

@dataclasses.dataclass
class ForeachBlockExtra:
    new_name: Name
    source: Reference

class NodeAttribute:
    class Name (enum.Enum):
        VALUE = enum.auto
        NAME = enum.auto
        TEXT = enum.auto
        SUBMIT_ON = enum.auto
    name: Name
    value: Constant

class NodeDefinitionExtra:
    class Type (enum.Enum):
        TEXT = enum.auto
        INPUT = enum.auto
        BUTTON = enum.auto
    type: Type

ViewDefinitionNodeExtra = Union [ForeachBlockExtra, NodeDefinitionExtra]

@dataclasses.dataclass
class ViewDefinitionNode:
    class Type (enum.Enum):
        FOREACH_BLOCK = enum.auto
        FORM_DEFINITION_BLOCK = enum.auto
        NODE_DEFINITION_BLOCK = enum.auto
        NODE_PROPERTY_DEFINITION_STMT = enum.auto
        IF_BLOCK = enum.auto
        ELSE_BLOCK = enum.auto
    type: Type
    extra: ViewDefinitionNodeExtra
    parent: Optional ["ViewDefinitionNode"]
    subnodes: List ["ViewDefinitionNode"] = dataclasses.field (default_factory = list)
    generates: List [Reference] = dataclasses.field (default_factory = list)
    references: List [Reference] = dataclasses.field (default_factory = list)

@dataclasses.dataclass
class View:
    name: Name
    definition_nodes: List [ViewDefinitionNode] = dataclasses.field (default_factory = list)

@dataclasses.dataclass
class AppDefinition:
    main_view: View = dataclasses.field (default = None) # ensured not None by end of AdvancedTransformer.transform call
    types: List [Type] = dataclasses.field (default_factory = list)
    instances: List [CompileTimeInstance] = dataclasses.field (default_factory = list)
    views: List [View] = dataclasses.field (default_factory = list)

def raise_out_of_context (_subitem: BasicItem, block_type: str): raise Exception (f"subitem with value '{_subitem.value}' seems to be out of context in a {block_type} block")