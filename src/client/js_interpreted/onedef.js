(async function (appUrl, config) {
    const print = console.log;

    // setting up parser
    var types = {};
    var instances = {};
    var unresolvedReferences = {};
    var parserContext = {};

    // loading file to parse
    var appDotOnedefResponse = await fetch (appUrl);
    var appDotOnedef = await appDotOnedefResponse.text ();
    // doing some basic preliminary parsing
    var appDotOnedefLines = appDotOnedef.split ("\n").filter (line => !line.trim ().startsWith ("#") && !(line.trim () == "")).map (line => {
        // count and remove indents
        var indentCount = 0;
        while (line.startsWith (config ["tab"])) {
            indentCount++;
            line = line.substr (config ["tab"].length);
        }

        // remove a comment at the end of the line
        // find last comment character
        // WARNING: MAX JANK! this will detect the character even if it's in a string or other definition
        // should probably add escape character in the future
        var commentStartPos = -1;
        for (var pos = line.length - 1; pos--; pos == 0) {
            if (line.charAt (pos) == config ["commentCharacter"]) {
                commentStartPos = pos;
                break;
            }
        }
        if (commentStartPos != -1) {
            line = line.substr (0, commentStartPos);
        }

        // trim off any extra whitespace from start/end
        line = line.trim ();
        return {indentCount: indentCount, contents: line};
    });

    // parse blocks and their corresponding lines
    var items = [];
    var blockStack = [];
    var getCurrentTopLevelItemList = () => {
        return blockStack.length == 0 ? items : blockStack [blockStack.length - 1] ["subitems"];
    };
    var reduceBlockStackToMatchIndentLevel = (targetIndentLevel) => {
        while (targetIndentLevel < blockStack.length) {
            var lastBlockStackItem = blockStack.pop ();
            if (lastBlockStackItem ["subitems"].length == 0) {
                throw "Empty block";
            }
            getCurrentTopLevelItemList ().push (lastBlockStackItem);
        }
    };
    for (var lineData of appDotOnedefLines) {
        var currentIndent = lineData ["indentCount"];
        var line = lineData ["contents"];
        if (currentIndent < blockStack.length) {
            reduceBlockStackToMatchIndentLevel (currentIndent);
        }
        if (line.endsWith (config ["blockStartCharacter"])) {
            blockStack.push ({
                type: "block",
                contents: line.substr (0, line.length - config ["blockStartCharacter"].length),
                subitems: []
            });
        } else {
            getCurrentTopLevelItemList ().push ({
                type: "statement",
                contents: line,
            });
        }
    }
    reduceBlockStackToMatchIndentLevel (0);
    console.log (JSON.stringify (items, null, 4));

    // define a method to visit each item, check for a matching regular expression, and call its associated handler function
    // (interpreterLevels is defined below this, since the included methods reference callsToVisitItem)
    var callsToVisitItem = [];
    var visitItem = (item, context) => {
        print (`visiting item with contents ${item ["contents"]}`);
        var matchingLevels = ["any", context ["data"] ["level"]];
        var allHandlers = [];
        for (var matchingLevel of matchingLevels) {
            var matchingLevelHandlers = interpreterLevels [matchingLevel] [item ["type"]];
            if (matchingLevelHandlers != undefined) {
                allHandlers = allHandlers.concat (matchingLevelHandlers);
            }
        }
        var matchingHandlerFound = false;
        for (var regexAndHandler of allHandlers) {
            var match = regexAndHandler [0] /* regex */.exec (item ["contents"]);
            if (match != null) {
                regexAndHandler [1] /* handler */ (item, context, match ["groups"]);
                matchingHandlerFound = true;
                break;
            }
        }
        if (!matchingHandlerFound) throw `Line "${item ["contents"]}" does not match any regular expressions for its type available globally or considering the current context level`;
        if (Object.keys (item).includes ("postVisitItem")) item ["postVisitItem"] ();
    };

    var visitAllSubitems = (item, newContext) => {
        for (var subitem of item ["subitems"]) {
            callsToVisitItem.unshift /* push to front (call next) */ ([subitem, newContext]);
        }
    };
    var addPostVisitSubitemsHook = (item, hook) => {
        item ["subitems"] [item ["subitems"].length - 1].postVisitItem = hook;
    };
    function generateChildContext (source, level, extraData) {
        var childContext = {
            data: {
                level: level,
                ...extraData
            },
            parent: source,
            children: []
        };
        source.children.push (childContext);
        return childContext;
    }
    function construct (name, type, extra) {
        var constructed = {
            type: type,
            synced: true
        };
        if (name == "Client") { // special hardcoded case since this is a mix of native + not

        }
        if (type ["data"] ["native"]) {
            switch (type ["data"] ["name"]) {
                case "String": break
                default: {
                    throw `Unimplemented constructor for native type ${type ["data"] ["name"]}`;
                }
            }
        } else {
            // construct all fields based on the info in type
            throw `Unimplemented: constructing non-native type`
        }
        instances [name] = constructed;
        return constructed;
    }
    function getMember (target, memberName) {

    }
    function setMember (target, memberName, memberValue) {

    }
    function deconstruct (target) {

    }
    function parseTypeName (context, typeName) {
        var genericMatch = /(?<genericSource>.+) of (?<genericTarget>.+)/.exec (typeName);
        if (genericMatch != null) {
            // yeah, it's recursive. sue me. will only get one level deep though, I don't expect (i hope) a generic of a generic, or more
            var genericTarget = parseTypeName (context, genericMatch.groups ["genericTarget"]);
            var genericSource = parseTypeName (context, genericMatch.groups ["genericSource"]);
            if (!genericSource ["data"] ["generic"]) throw "Using non-generic as generic source"
            var generic = {...genericSource}; // makes (shallow) copy of genericSource
            generic ["target"] = genericTarget;
            return generic;
        } else {
            var toConsider = [];
            function addAliasesAndObjectsFromContext (targetContext) {
                for (var contextChild of targetContext ["children"]) {
                    if (["aliasDefinition", "typeDefinition"].includes (contextChild ["data"] ["level"])) {
                        if (!(toConsider.includes (contextChild))) {
                            toConsider.push (contextChild);
                        }
                    }
                }
            }
            var currentContext = context;
            do {
                print ("adding from current ctx, not top");
                addAliasesAndObjectsFromContext (currentContext);
                currentContext = currentContext ["parent"];
            } while (currentContext != null /* parent of top is null */);
            print (`to consider size: ${toConsider.length}`);
            for (var toConsiderItem of toConsider) {
                print (`name of item: ${toConsiderItem ["data"] ["name"]}`);
                if (toConsiderItem ["data"] ["name"] == typeName) {
                    return toConsiderItem ["data"] ["level"] == "aliasDefinition"
                        ? toConsiderItem ["data"] ["target"]
                        : toConsiderItem;
                }
            }
            throw `Unable to parse type name "${typeName}"`;
        }
    }
    var interpreterLevels = { // maps context level name (any is special, will be combined with actual current) to dict
        "any": { // maps type of item to list
            "block": [ // regular expression, function that handles result
                [/pass_block/, function (item, context, matchGroups) {}], // pass_block:
                [/(?<side>.+) side/, function (item, context, matchGroups) {
                    if (matchGroups ["side"] == config ["side"]) {
                        visitAllSubitems (item, context /* use same context */);
                    }
                }] // client side:
            ],
            "statement": [
                [/pass/, function (item, context, matchGroups) {}], // pass
                [/alias (?<aliasName>.+) is (?<aliasTarget>.+)/, function (item, context, matchGroups) {
                    var aliasTarget = parseTypeName (context, matchGroups ["aliasTarget"]);
                    generateChildContext (context, "aliasDefinition", {
                        name: matchGroups ["aliasName"],
                        target: aliasTarget
                    });
                }] // define alias TodoListItem as String
            ]
        },
        "top": {
            "block": [
                [/type (?<name>.+)/, function (item, context, matchGroups) {
                    var name = matchGroups ["name"];
                    var typeDefinitionContext = generateChildContext (context, "typeDefinition", {
                        name: name,
                        native: false
                    });
                    visitAllSubitems (item, typeDefinitionContext);
                }] // object User:
            ],
            "statement": [
                [/instance (?<name>.+) is (?<typeName>.+)/, function (item, context, matchGroups) {
                    var type = parseTypeName (context, matchGroups ["typeName"]);
                    construct (matchGroups ["name"], type, {});
                }]
            ]
        }, // top level in the file, inside no (context-manipulating) blocks
        "typeDefinition": {
            "block": [
                [/fields/, function (item, context, matchGroups) {
                    var typeFieldsDefinitionContext = generateChildContext (context, "typeFieldsDefinition", {});
                    addPostVisitSubitemsHook (item, () => {
                        context ["data"] ["fields"] = [];
                        for (var childContext of context ["children"]) {
                            if (childContext ["data"] ["level"] != "typeFieldsDefinition") throw "Context is child of fields with unknown level";
                            context ["data"] ["fields"].push ({
                                name: childContext ["data"] ["name"],
                                type: childContext ["data"] ["type"]
                            });
                        }
                    });
                    visitAllSubitems (item, typeFieldsDefinitionContext);
                }] // fields:
            ]
        }, // inside type xyz: block
        "typeFieldsDefinition": {
            "block": [
                [/(?<name>.+) is (?<typeName>.+)/, function (item, context, matchGroups) {
                    var typeFieldDefinitionContext = generateChildContext (context, "typeFieldDefinition", {
                        name: matchGroups ["name"],
                        type: parseTypeName (context, matchGroups ["typeName"])
                    });
                    print (`added field ${matchGroups ["name"]} (block)`);
                    visitAllSubitems (item, typeFieldDefinitionContext);
                }]
            ],
            "statement": [
                [/(?<name>.+) is (?<typeName>.+)/, function (item, context, matchGroups) {
                    generateChildContext (context, "typeFieldDefinition", {
                        name: matchGroups ["name"],
                        type: parseTypeName (context, matchGroups ["typeName"])
                    });
                    print (`added field ${matchGroups ["name"]} (stmt)`);
                }]
            ]
        }, // inside fields: block
        "typeFieldDefinition": {} // inside xyz is X with Y: block
        // (etc...)
    };

    var topLevelContext = {
        data: {
            level: "top"
        },
        parent: null,
        children: []
    };

    // natives
    function addNative (nativeName, generic) {
        generateChildContext (topLevelContext, "typeDefinition", {
            name: nativeName,
            native: true,
            generic: generic
        });
    }
    addNative ("String", false);
    addNative ("List", true);
    addNative ("Linkage", true);
    generateChildContext (topLevelContext, "typeDefinition", {
        name: "Client",
        native: true /* kinda. really we should have a separate 'hasFields' or something */
    });

    // add each top level item to the list of items to visit
    for (var topLevelItem of items) {
        callsToVisitItem.push ([topLevelItem, topLevelContext]);
    }

    // data relevant at application runtime (now)
    var instances = {};

    // visit all items
    // (note: more items will be added to callsToVisitItem by calls to visitItem)
    while (callsToVisitItem.length != 0) {
        var callToVisitItem = callsToVisitItem.shift () /* remove first item */;
        visitItem (callToVisitItem [0], callToVisitItem [1]);
    }

    console.log (`top level context now has ${children.length} children`);
}) (document.currentScript.getAttribute ("onedef-app-url"), {
    tab: "    ", // four spaces
    commentCharacter: '#', // default is hashtag
    blockStartCharacter: ':', // comes at the end of a line that starts a block
    side: "client" // used to check if we should parse "side xyz:" blocks
});
