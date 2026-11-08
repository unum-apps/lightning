const test = require("node:test");
const assert = require("node:assert");

const Flow = require("../www/js/flow.js");

const ROD = {id: "shop-at:rod.lightning:test", name: "Shop at", input: {location: "str"}};

test("an id is a string with no slash, like the ones the API gives", () => {
    const id = new RegExp(Flow.ID);

    assert.ok(id.test("eat-well:bolt.lightning:test"));
    assert.ok(id.test("1:strike.lightning:test"));
    assert.ok(!id.test("a/b"));
    assert.ok(!id.test("create"));
    assert.ok(!id.test(""));
});

test("a Rod asks for the inputs it names", () => {
    assert.deepStrictEqual(Flow.inputs(ROD), [{name: "location", kind: "str"}]);
    assert.deepStrictEqual(Flow.inputs({id: "x", name: "X"}), []);
});

test("a Strike says what the Rod is and what was given", () => {
    assert.strictEqual(Flow.description(ROD, {location: "Shaws"}), "Shop at (location: Shaws)");
    assert.strictEqual(Flow.description(ROD, {location: ""}), "Shop at");
    assert.strictEqual(Flow.description(ROD, undefined), "Shop at");
});

test("striking a Rod makes a created Strike from it", () => {
    assert.deepStrictEqual(Flow.strike(ROD, {location: "Shaws"}, "gaf:entity.cumulus:test"), {
        entity_id: "gaf:entity.cumulus:test",
        description: "Shop at (location: Shaws)",
        rod_id: "shop-at:rod.lightning:test",
        state: "created"
    });
});

test("a Strike goes from created to in progress to done, and no further", () => {
    assert.strictEqual(Flow.next({state: "created"}), "in progress");
    assert.strictEqual(Flow.next({state: "in progress"}), "done");
    assert.strictEqual(Flow.next({state: "done"}), null);
});

test("only the Strikes not done are open", () => {
    const strikes = [{id: "1", state: "created"}, {id: "2", state: "done"}, {id: "3", state: "in progress"}];

    assert.deepStrictEqual(Flow.open(strikes).map(strike => strike.id), ["1", "3"]);
});

test("the flow page renders the Rods, the inputs and the open Strikes", () => {
    const fs = require("node:fs");
    const doT = require("../www/js/doT.js");

    const page = fs.readFileSync(__dirname + "/../www/flow.html", "utf8")
        .replace("{{#def.Header}}", "").replace("{{#def.Footer}}", "");
    const render = doT.template(page, Object.assign({}, doT.templateSettings, {strip: false}));

    const html = render({
        rods: [ROD],
        rod: ROD,
        inputs: Flow.inputs(ROD),
        entity_id: "gaf:entity.cumulus:test",
        strikes: [{id: "1:strike.lightning:test", description: "Shop at (location: Shaws)", state: "created"}]
    });

    assert.match(html, /<option value="shop-at:rod.lightning:test" selected>Shop at<\/option>/);
    assert.match(html, /id="input__location"/);
    assert.match(html, /value="gaf:entity.cumulus:test"/);
    assert.match(html, /Shop at \(location: Shaws\)/);
    assert.match(html, /Start/);
});
