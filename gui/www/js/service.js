DRApp.route("home", "/", "Home", "Base", "home");

DRApp.models = DRApp.rest("GET", "api/model")["models"];

// The ids here are strings with no slash, not numbers, so the routes that take an id match those

DRApp.model = function(model) {

    DRApp.controller(model.title, "Model", {
        model: model
    });

    DRApp.route(model.singular + "_list", "/" + model.singular, "List", model.title, "list");
    DRApp.route(model.singular + "_create", "/" + model.singular + "/create", "Create", model.title, "create");

    if (model.id) {
        DRApp.route(model.singular + "_retrieve", "/" + model.singular + "/{id:" + Flow.ID + "}", "Retrieve", model.title, "retrieve");
        DRApp.route(model.singular + "_update", "/" + model.singular + "/{id:" + Flow.ID + "}/update", "Update", model.title, "update");
    }

};

// The Rod and Strike flow: strike a Rod to make a Strike, then work the open Strikes to done

DRApp.controller("Flow", "Base", {
    rods: [],
    strikes: [],
    flow: function() {
        this.rods = DRApp.rest("GET", "api/model/rod")["rods"];
        this.strikes = DRApp.rest("GET", "api/model/strike")["strikes"];
        this.it = {rods: this.rods, strikes: Flow.open(this.strikes), rod: null, inputs: [], entity_id: $.cookie("entity_id") || ""};
        DRApp.render(this.it);
    },
    pick: function() {
        var id = $("#rod").val();
        this.it.entity_id = $("#entity_id").val() || this.it.entity_id;
        this.it.rod = this.rods.filter(function(rod) { return rod.id == id; })[0] || null;
        this.it.inputs = this.it.rod ? Flow.inputs(this.it.rod) : [];
        DRApp.render(this.it);
    },
    strike: function() {
        var values = {};
        for (var index = 0; index < this.it.inputs.length; index++) {
            values[this.it.inputs[index].name] = $("#input__" + this.it.inputs[index].name).val();
        }
        var entity_id = $("#entity_id").val();
        $.cookie("entity_id", entity_id);
        DRApp.rest("POST", "api/model/strike", {strike: Flow.strike(this.it.rod, values, entity_id)});
        this.flow();
    },
    advance: function(id) {
        var strike = this.strikes.filter(function(strike) { return strike.id == id; })[0];
        DRApp.rest("PATCH", "api/model/strike/" + id, {strike: {state: Flow.next(strike)}});
        this.flow();
    }
});

DRApp.template("Flow", DRApp.load("flow"), null, DRApp.partials);
DRApp.route("flow", "/flow", "Flow", "Flow", "flow");

DRApp.attach();
