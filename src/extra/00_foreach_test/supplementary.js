function variable_instantiate (proto) {
    switch (proto.type) {
        case "native": {
            return {
                proto: proto,
                value: proto.default,
            }
        }
        case "list": {
            return {
                proto: proto,
                variables: {},
                last_id: -1,
                bound_foreach_instances: []
            }
        }
        case "custom": {
            let instance = {
                proto: proto,
                props: {}
            };
            for (let prop_name of Object.keys (proto.props)) {
                instance [prop_name] = variable_instantiate (proto.props [prop_name])
            }
            return instance;
        }
        default: throw `instantiating unimplemented for variable type ${proto.type}`;
    }
}

function variable_cleanup (instance) {
    switch (instance.proto.type) {
        case "native": {
            return;
        }
        case "list": {
            for (let variable_id of Object.keys (instance.variables)) {
                variable_cleanup (instance.variables [variable_id]);
            }
            return;
        }
        case "custom": {
            for (let prop_name of Object.keys (instance.props)) {
                variable_cleanup (instance.props [prop_name]);
            }
            return;
        }
        default: throw `cleaning up unimplemented for variable type ${instance.proto.type}`;
    }
}

function list_add (list_instance) {
    if (!(list_instance.proto.type === "list")) throw "calling add on non-list instance";
    let new_instance = variable_instantiate (list_instance.proto.sub);
    list_instance.variables [++list_instance.last_id] = new_instance;
    return new_instance;
}

function view_node_instantiate (proto, parent_instance) {
    switch (proto.type) {
        default: throw `instantiating unimplemented for view node type ${proto.type}`;
    }
}

function view_node_cleanup (instance) {
    switch (instance.proto.type) {
        default: throw `instantiating unimplemented for view node type ${instance.proto.type}`;
    }
}