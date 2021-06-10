/*
IMPLEMENTING THE FOLLOWING ONEDEF FILE

alias Bottom is List of String
type Middle:
    fields:
        bottom is Bottom
alias Top is List of Middle
instance top is Top
view Main:
    foreach middle in top:
        foreach string in middle.bottom:
            node text:
                value string
*/



let bottom_variable_proto = { // alias Bottom is List of String
    type: "list",
    sub: {
        type: "native",
        default: "bruh"
    }
};

let middle_variable_proto = { // type Middle: fields: bottom is Bottom
    type: "custom",
    props: {
        bottom: bottom_variable_proto
    }
};

let top_variable_proto = { // alias Top is List of Middle
    type: "list",
    sub: middle_variable_proto
};


let top_variable_instance = variable_instantiate (top_variable_proto);
let middle_variable_instance = list_add (top_variable_instance);
let bottom_variable_instance = middle_variable_instance ["bottom"];
let string = list_add (bottom_variable_instance);
console.log (string.value);



let main_view_node_proto = { // view Main:
    type: "container", /* direct passthrough, instantiates one of each sub */
    parent: null,
    subs: [] /* gets pushed */
};

let top_foreach_view_node_proto = { // foreach middle in top:
    type: "foreach", /* instantiates body for each item in the list variable it's bound to */
    bound_to: { /* ref to list instance */
        type: "direct", /* refers to a direct instance */
        direct: top_variable_instance
    },
    body: null, /* gets assigned */
    parent: main_view_node_proto,
};
main_view_node_proto.subs.push (top_foreach_view_node_proto);

let top_foreach_body_view_node_proto = { // (body of) foreach middle in top:
    type: "foreach_body", /* container for nodes to be assigned to an id in the associated list */
    subs: []
};
top_foreach_view_node_proto.body = top_foreach_body_view_node_proto;

let middle_foreach_view_node_proto = { // foreach string in middle.bottom:
    type: "foreach",
    bound_to: { /* ref to list instance */
        type: "upper_prop", /* refers to a named property of a loop variable defined by a foreach higher in the tree */
        tree_walk_index: 0, /* the next highest foreach in the tree, higher indices mean we need to walk higher */
        prop_name: "bottom"
    },
    body: null, /* gets assigned */
    parent: top_foreach_view_node_proto
};
top_foreach_body_view_node_proto.subs.push (middle_foreach_view_node_proto);

let middle_foreach_body_view_node_proto = { // (body of) foreach string in middle.bottom:
    type: "foreach_body",
    subs: []
};
middle_foreach_view_node_proto.body = middle_foreach_body_view_node_proto;

let bottom_display_view_node_proto = { // node text: value string
    type: "display", /* displays info from the referenced instance */
    subtype: "text", /* displays string in a <p> node */
    value: { /* ref to instance used as value */
        type: "upper", /* refers (directly) to a loop variable defined by a foreach higher in the tree */
        tree_walk_index: 0 /* same meaning as in middle_foreach_view_node_proto */
    },
    parent: middle_foreach_view_node_proto
};
middle_foreach_body_view_node_proto.subs.push (bottom_display_view_node_proto);


let main_view_node_instance = view_node_instantiate (main_view_node_proto);

window.addEventListener ("beforeunload", () => {variable_cleanup (top_variable_instance)});