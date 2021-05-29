import enum, dataclasses
from typing import Union, List, Optional

Line = str
# input, post basic transformations
Source = List [Line]

@dataclasses.dataclass
class LineWithIndentCount:
    line: str
    indent_count: int

# post indent read
SourceWithIndentCount = List [LineWithIndentCount]

# post block definition
@dataclasses.dataclass
class BasicStatementItem:
    value: str
    parent: Optional [Union ["BasicStatementItem", "BasicBlockItem"]]

@dataclasses.dataclass
class BasicBlockItem:
    value: str
    parent: Optional [Union ["BasicStatementItem", "BasicBlockItem"]]
    subitems: List [Union [BasicStatementItem, "BasicBlockItem"]] = dataclasses.field (default_factory = list)

BasicItem = Union [BasicBlockItem, BasicStatementItem]
BasicList = List [BasicItem]

# post advanced pass
class ItemType (enum.Enum):
    type_definition = enum.auto # type TodoEntry:
    fields_definition = enum.auto # fields:
    field_definition = enum.auto # value is String
    actions_definition = enum.auto # actions:
    action_definition = enum.auto # construct:
    action_body_part = enum.auto # self.value = payload.value, etc
    instance_definition = enum.auto # instance todos is List of String
    view_definition = enum.auto # view TodoListEditor:
    view_body_part = enum.auto # foreach todo in todos:, etc
    main_view_definition = enum.auto # main view TodoListEditor

@dataclasses.dataclass
class AdvancedStatementItem:
    type: ItemType
    attribs: dict # attributes specific to the given type
    parent: Optional [Union ["AdvancedStatementItem", "AdvancedBlockItem"]]

@dataclasses.dataclass
class AdvancedBlockItem:
    type: ItemType
    attribs: dict # attributes specific to the given type
    parent: Optional [Union [AdvancedStatementItem, "AdvancedBlockItem"]]
    subitems: List [Union [AdvancedStatementItem, "AdvancedBlockItem"]] = dataclasses.field (default_factory = list)

AdvancedItem = Union [AdvancedStatementItem, AdvancedBlockItem]
AdvancedList = List [AdvancedItem]

# types used in config
CommentSpecifier = str
IndentSpecifier = str
BlockSpecifier = str