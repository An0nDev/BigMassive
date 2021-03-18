(async function (appUrl, config) {
    // setting up parser
    var types = {};
    var instances = {};
    var unresolvedReferences = {};
    var parserContext = {};

    // loading file to parse
    var appBmResponse = await fetch (appUrl);
    var appBm = await appBmResponse.text ();
    // doing some basic preliminary parsing
    var appBmLines = appBm.split ("\n").filter (line => !line.trim ().startsWith ("#") && !(line.trim () == "")).map (line => {
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
    for (var lineData of appBmLines) {
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
        if (Object.keys (item).includes ("postVisitItem")) { item ["postVisitItem"] (); }
    };

    var visitAllSubitems = (item, newContext) => {
        for (var subitem of item ["subitems"]) {
            callsToVisitItem.unshift /* push to front (call next) */ ([subitem, newContext]);
        }
    };
    var addPostVisitSubitemsHook = (item, hook) => {
        item ["subitems"] [item ["subitems"].length - 1].postVisitItem = hook;
    };
    var interpreterLevels = { // maps context level name (any is special, will be combined with actual current) to dict
        "any": { // maps type of item to list
            "block": [ // regular expression, function that handles result
                [/(?<side>.+) side/, function (item, context, matchGroups) {
                    if (matchGroups ["side"] == config ["side"]) {
                        visitAllSubitems (item, context /* use same context */);
                    }
                }] // client side:
            ],
            "statement": [
                [/pass/, function (item, context, matchGroups) {}], // pass
                [/define alias (?<aliasName>.+) as (?<aliasTarget>.+)/, function (item, context, matchGroups) {
                    var aliasTarget;

                    // parse generic (x of y)
                    var genericMatch = /(?<genericSource>.+) of (?<genericTarget>.+)/.exec (matchGroups ["aliasTarget"]);
                    if (genericMatch != null) {
                        var genericTarget = findInScope ("object", genericMatch.groups ["genericTarget"]);
                        var genericSource = findInScope ("object", genericMatch.groups ["genericSource"]);
                        if (genericSource ["type"] != "generic") throw "Using non-generic as generic source"
                        var generic = {...genericSource}; // makes (shallow) copy of genericSource
                        generic ["target"] = genericTarget;
                        aliasTarget = generic;
                    } else {
                        aliasTarget = findInScope ("object", matchGroups ["aliasTarget"]);
                    }

                    getCurrentScope ["objects"] [matchGroups ["aliasName"]] = aliasTarget;
                }] // define alias TodoListItem as String
            ]
        },
        "top": {
            "block": [

            ],
            "statement": [

            ]
        },
        "objectDefinition": {}, // inside object xyz: block
        "objectFieldsDefinition": {}, // inside fields: block
        "objectFieldDefinition": {} // inside xyz is X with Y: block
        // (etc...)
    };

    // add each top level item to the list of items to visit
    for (var topLevelItem of items) {
        callsToVisitItem.push ([topLevelItem, {
            data: {
                level: "top"
            },
            parents: []
        }]);
    }

    // visit all items
    // (note: more items will be added to callsToVisitItem by calls to visitItem)
    while (callsToVisitItem.length != 0) {
        var callToVisitItem = callsToVisitItem.shift () /* remove first item */;
        visitItem (callToVisitItem [0], callToVisitItem [1]);
    }
}) (document.currentScript.getAttribute ("bm-app-url"), {
    tab: "    ", // four spaces
    commentCharacter: '#', // default is hashtag
    blockStartCharacter: ':', // comes at the end of a line that starts a block
    side: "client" // used to check if we should parse "side xyz:" blocks
});
