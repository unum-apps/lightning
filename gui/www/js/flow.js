// The Rod and Strike flow: pick a Rod, give what it asks for, make the Strike, and work it to done. The parts that
// decide something are here so they can be tested without a browser

var Flow = {

    // An id is a string of letters, digits, dots, colons and dashes, like eat-well:bolt.lightning:test, not a number, and
    // not the create route. The pattern has no slash and no colon in it, because a route is split on both, so the
    // colon is written as \x3a

    ID: "^(?!create$)[\\w.\\x3a-]+$",

    // The state a Strike goes to next

    NEXT: {"created": "in progress", "in progress": "done"},

    // What a Rod asks for, from the inputs it names

    inputs: function(rod) {
        var input = rod.input || {};
        return Object.keys(input).map(function(name) {
            return {name: name, kind: input[name]};
        });
    },

    // What a Strike says it is: the Rod, and what was given for each of its inputs

    description: function(rod, values) {
        values = values || {};
        var given = Object.keys(values).filter(function(name) {
            return values[name] !== "";
        }).map(function(name) {
            return name + ": " + values[name];
        });
        return given.length ? rod.name + " (" + given.join(", ") + ")" : rod.name;
    },

    // The Strike a Rod makes when it is struck

    strike: function(rod, values, entity_id) {
        return {
            entity_id: entity_id,
            description: Flow.description(rod, values),
            rod_id: rod.id,
            state: "created"
        };
    },

    // Where a Strike goes next, or null when it is done

    next: function(strike) {
        return Flow.NEXT[strike.state] || null;
    },

    // The Strikes that are not done

    open: function(strikes) {
        return strikes.filter(function(strike) {
            return strike.state != "done";
        });
    }

};

if (typeof module !== "undefined") {
    module.exports = Flow;
}
