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
class ActionDefinitionNode:
    class Type (enum.Enum):
        ASSIGNMENT_STMT = enum.auto
        PASS_STMT = enum.auto
    type: Type
    references: List ["Instance"]

@dataclasses.dataclass
class Action:
    name: Name
    definition_nodes: List [ActionDefinitionNode]

@dataclasses.dataclass
class NativeType: pass

@dataclasses.dataclass
class UserDefinedType:
    name: Name
    fields: List [Field] = dataclasses.field (default_factory = list)
    actions: List [Action] = dataclasses.field (default_factory = list)

Type = Union [NativeType, UserDefinedType]

@dataclasses.dataclass
class CompileTimeInstance:
    name: Name
    type: Type
    fields: List ["Instance"]
    parent: Optional ["Instance"]

@dataclasses.dataclass
class RuntimeInstance:
    name: Name
    type: Type
    value: Optional [CompileTimeInstance]

Instance = Union [CompileTimeInstance, RuntimeInstance]

@dataclasses.dataclass
class ViewDefinitionNode:
    class Type (enum.Enum):
        FOREACH_BLOCK = enum.auto
        NODE_DEFINITION_BLOCK = enum.auto
        NODE_PROPERTY_DEFINITION_STMT = enum.auto
        IF_BLOCK = enum.auto
        ELSE_BLOCK = enum.auto
    type: Type
    references: List [Instance]

@dataclasses.dataclass
class View:
    name: Name
    definition_nodes: List [ViewDefinitionNode]

@dataclasses.dataclass
class AppDefinition:
    main_view: View = dataclasses.field (default = None) # ensured not None by end of AdvancedTransformer.transform call
    types: List [Type] = dataclasses.field (default_factory = list)
    instances: List [CompileTimeInstance] = dataclasses.field (default_factory = list)
    views: List [View] = dataclasses.field (default_factory = list)
