from .advanced_common import *

ConstructSignature = Signature (is_static = True, arguments = [], has_return_value = False)
EditSignature = Signature (is_static = False, arguments = ["_0"], has_return_value = False)
Builtins: List [NativeType] = [
    NativeType (name = "String", actions = [
        NativeAction (name = "construct", signature = ConstructSignature, native_implementations = {
            Platform.CLIENT_JS: [
                "return String ();"
            ],
            Platform.SERVER_PY: [
                "return []"
            ]
        }),
        NativeAction (name = "edit", signature = EditSignature, native_implementations = {
            Platform.CLIENT_JS: [
                "self = _0;"
            ],
            Platform.SERVER_PY: [
                "self = _0"
            ]
        }),
    ]),
    NativeType (name = "Boolean", actions = [
        NativeAction (name = "construct", signature = ConstructSignature, native_implementations = {
            Platform.CLIENT_JS: [
                "return false;"
            ],
            Platform.SERVER_PY: [
                "return False"
            ]
        }),
        NativeAction (name = "edit", signature = EditSignature, native_implementations = {
            Platform.CLIENT_JS: [
                "self = _0"
            ],
            Platform.SERVER_PY: [
                "self = _0;"
            ]
        }),
    ]),
    GenericType (name = "List", actions = [
        NativeAction (name = "construct", signature = ConstructSignature, native_implementations = {
            Platform.CLIENT_JS: [
                "return object ();"
            ],
            Platform.SERVER_PY: [
                "return {}"
            ]
        }),
        NativeAction (name = "add", signature = Signature (is_static = False, arguments = None, has_return_value = True), native_implementations = {
            Platform.CLIENT_JS: [
                SpecialNativeImplementationLine (
                    prefix = "let newUniqueID = ",
                    type = SpecialNativeImplementationLine.Type.GET_NEXT_UNIQUE_ID,
                    suffix = ";"
                ),
                SpecialNativeImplementationLine (
                    prefix = "self [newUniqueID] = ",
                    type = SpecialNativeImplementationLine.Type.CALL_GENERIC_TARGET_CTOR,
                    suffix = ";"
                )
            ],
            Platform.SERVER_PY: [
                SpecialNativeImplementationLine (
                    prefix = "new_unique_id = ",
                    type = SpecialNativeImplementationLine.Type.GET_NEXT_UNIQUE_ID,
                    suffix = ""
                ),
                SpecialNativeImplementationLine (
                    prefix = "self [new_unique_id] = ",
                    type = SpecialNativeImplementationLine.Type.CALL_GENERIC_TARGET_CTOR,
                )
            ]
        }),
        NativeAction (name = "remove", signature = Signature (is_static = False, arguments = ["target"], has_return_value = False), native_implementations = {
            Platform.CLIENT_JS: [
                "delete self [target];"
            ],
            Platform.SERVER_PY: [
                "del self [target]"
            ]
        })
    ])
]