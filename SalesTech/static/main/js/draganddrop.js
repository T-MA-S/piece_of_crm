function init() {

    var icons = {
        "home":
            "M32 18.451l-16-12.42-16 12.42v-5.064l16-12.42 16 12.42zM28 18v12h-8v-8h-8v8h-8v-12l12-9z",

        "droplet":
            "M27.998 19.797c-0-0.022-0.001-0.044-0.001-0.066-0.001-0.045-0.002-0.089-0.004-0.134-0.313-9.864-11.993-19.597-11.993-19.597s-11.68 9.733-11.993 19.598c-0.001 0.045-0.003 0.089-0.004 0.134-0 0.022-0.001 0.044-0.001 0.066-0.001 0.067-0.002 0.135-0.002 0.203 0 0.074 0.001 0.148 0.002 0.221 0 0.006 0 0.012 0 0.018 0.127 6.517 5.45 11.76 11.997 11.76s11.87-5.244 11.997-11.761c0-0.006 0-0.012 0-0.018 0.001-0.074 0.002-0.147 0.002-0.221 0-0.068-0.001-0.136-0.002-0.203zM23.998 20.148l-0 0.013c-0.041 2.103-0.892 4.073-2.395 5.548-1.504 1.477-3.495 2.291-5.604 2.291-0.389 0-0.775-0.028-1.154-0.082 4.346-2.589 7.257-7.335 7.257-12.76 0-0.608-0.037-1.207-0.108-1.796 1.259 2.311 1.939 4.462 2 6.363l0 0.005c0.001 0.030 0.002 0.059 0.002 0.089l0.001 0.045c0.001 0.046 0.002 0.091 0.002 0.137 0 0.049-0.001 0.099-0.002 0.148z",
    }

    // Since 2.2 you can also author concise templates with method chaining instead of GraphObject.make
    // For details, see https://gojs.net/latest/intro/buildingObjects.html
    const $ = go.GraphObject.make;  // for conciseness in defining templates

    myDiagram =
        $(go.Diagram, "myDiagramDiv",  // must name or refer to the DIV HTML element
            {
                grid: $(go.Panel, "Grid",
                    $(go.Shape, "LineH", { stroke: "lightgray", strokeWidth: 0.5 }),
                    $(go.Shape, "LineH", { stroke: "gray", strokeWidth: 0.5, interval: 10 }),
                    $(go.Shape, "LineV", { stroke: "lightgray", strokeWidth: 0.5 }),
                    $(go.Shape, "LineV", { stroke: "gray", strokeWidth: 0.5, interval: 10 })
                ),
                "draggingTool.dragsLink": true,
                "draggingTool.isGridSnapEnabled": true,
                "linkingTool.isUnconnectedLinkValid": true,
                "linkingTool.portGravity": 20,
                "relinkingTool.isUnconnectedLinkValid": true,
                "relinkingTool.portGravity": 20,
                "relinkingTool.fromHandleArchetype":
                    $(go.Shape, "Diamond", { segmentIndex: 0, cursor: "pointer", desiredSize: new go.Size(8, 8), fill: "tomato", stroke: "darkred" }),
                "relinkingTool.toHandleArchetype":
                    $(go.Shape, "Diamond", { segmentIndex: -1, cursor: "pointer", desiredSize: new go.Size(8, 8), fill: "darkred", stroke: "tomato" }),
                "linkReshapingTool.handleArchetype":
                    $(go.Shape, "Diamond", { desiredSize: new go.Size(7, 7), fill: "lightblue", stroke: "deepskyblue" }),
                "rotatingTool.handleAngle": 270,
                "rotatingTool.handleDistance": 30,
                "rotatingTool.snapAngleMultiple": 15,
                "rotatingTool.snapAngleEpsilon": 15,
                "undoManager.isEnabled": true,
                'allowHorizontalScroll': false,
                'allowVerticalScroll': false
            });

    // when the document is modified, add a "*" to the title and enable the "Save" button
    myDiagram.addDiagramListener("DocumentBoundsChanged", e => {
        var emailbutton = document.getElementById("addEmailButton");
        var telegrambutton = document.getElementById("addTelegramButton");
        var delaybutton = document.getElementById("addDelayButton");
        var goalbutton = document.getElementById("addGoalButton");
        var triggerbutton = document.getElementById("addTriggerButton");
        var diagram_json = JSON.parse(myDiagram.model.toJson());
        var draganddropjson = JSON.parse(document.getElementById('draganddropjson_for_data').value);

        for (let [key, value] of Object.entries(diagram_json.nodeDataArray)) {
            var keys = [];
            var node = myDiagram.findNodeForKey(value.key);

            if (Object.values(draganddropjson).length != 0) {
                for (let [k, v] of Object.entries(draganddropjson)) { keys.push(Object.keys(v)[0]); }
            }
            if (!(keys.includes(String(value.key)))) {
                switch (Object.keys(value.customData)[0]) {
                    case "EMAIL_TEMPLATE":
                        emailformreset();
                        setbuttonattributes(diagram_json, emailbutton, value.key)
                        set_data(draganddropjson_for_data, 'email', value.key)
                        emailbutton.click();
                        add_draganddrgopjson_default("EMAIL_TEMPLATE")
                        break;
                    case "TELEGRAM":
                        telegramformreset();
                        setbuttonattributes(diagram_json, telegrambutton, value.key)
                        set_data(draganddropjson_for_data, 'telegram', value.key)
                        telegrambutton.click();
                        add_draganddrgopjson_default("TELEGRAM")
                        break;
                    case "DELAY":
                        delayformreset();
                        setbuttonattributes(diagram_json, delaybutton, value.key)
                        set_data(draganddropjson_for_data, 'delay', value.key)
                        delaybutton.click();
                        add_draganddrgopjson_default("DELAY")
                        break;
                    case "GOAL":
                        goalformreset();
                        setbuttonattributes(diagram_json, goalbutton, value.key)
                        set_data(draganddropjson_for_data, 'goal', value.key)
                        goalbutton.click();
                        add_draganddrgopjson_default("GOAL")
                        break;

                    case "TRIGGER":
                        if (!draganddropjson.length) {
                            show_trigger_first_alert();
                            diagram_delete_node(myDiagram, node)
                            break
                        } else if (diagram_json.nodeDataArray.at(-2).text === 'Telegram') {
                            show_trigger_error_alert(diagram_json.nodeDataArray.at(-2).text);
                            diagram_delete_node(myDiagram, node)
                            break
                        } else if (diagram_json.nodeDataArray.at(-2).text === 'Delay') {
                            show_trigger_error_alert(diagram_json.nodeDataArray.at(-2).text);
                            diagram_delete_node(myDiagram, node)
                            break
                        } else if (diagram_json.nodeDataArray.at(-2).text === 'Goal') {
                            show_trigger_error_alert(diagram_json.nodeDataArray.at(-2).text);
                            diagram_delete_node(myDiagram, node)
                            break
                        }
                        triggerformreset();
                        setbuttonattributes(diagram_json, triggerbutton, value.key);
                        set_data(draganddropjson_for_data, 'trigger', value.key)
                        triggerbutton.click();
                        add_draganddrgopjson_default("TRIGGER")
                        break;
                }
            }
        }
    });


    myDiagram.addDiagramListener("ExternalObjectsDropped", e => {
        e.subject.each(part => {
            if (part instanceof go.Node) {
                const droppt = e.diagram.lastInput.documentPoint;
                const nearby = e.diagram.findPartsNear(droppt, 400);  // ignore nodes that are far away
                let dist = Infinity;
                let closest = null;
                nearby.each(part => {
                    if (part instanceof go.Node &&
                        !part.isSelected &&  // don't include dropped nodes!
                        part.actualBounds.center.distanceSquaredPoint(droppt) < dist) {
                        dist = part.actualBounds.center.distanceSquaredPoint(droppt);
                        closest = part;
                    }
                });
                if (closest !== null) {
                    if (closest.data != null) {
                        e.diagram.model.addLinkData({ from: closest.data.key, to: part.data.key });
                    }
                }
            }
        });
    });


    // Define a function for creating a "port" that is normally transparent.
    // The "name" is used as the GraphObject.portId, the "spot" is used to control how links connect
    // and where the port is positioned on the node, and the boolean "output" and "input" arguments
    // control whether the user can draw links from or to the port.
    function makePort(name, spot, output, input) {
        // the port is basically just a small transparent circle
        return $(go.Shape, "Circle",
            {
                fill: null,  // not seen, by default; set to a translucent gray by showSmallPorts, defined below
                stroke: null,
                desiredSize: new go.Size(7, 7),
                alignment: spot,  // align the port on the main Shape
                alignmentFocus: spot,  // just inside the Shape
                portId: name,  // declare this object to be a "port"
                fromSpot: spot, toSpot: spot,  // declare where links may connect at this port
                fromLinkable: output, toLinkable: input,  // declare whether the user may draw links to/from here
                cursor: "pointer"  // show a different cursor to indicate potential link point
            });
    }

    var nodeSelectionAdornmentTemplate =
        $(go.Adornment, "Auto",
            $(go.Shape, { fill: null, stroke: "deepskyblue", strokeWidth: 1.5, strokeDashArray: [4, 2] }),
            $(go.Placeholder)
        );

    var nodeResizeAdornmentTemplate =
        $(go.Adornment, "Spot",
            { locationSpot: go.Spot.Right },
            $(go.Placeholder),
            $(go.Shape, { alignment: go.Spot.TopLeft, cursor: "nw-resize", desiredSize: new go.Size(6, 6), fill: "lightblue", stroke: "deepskyblue" }),
            $(go.Shape, { alignment: go.Spot.Top, cursor: "n-resize", desiredSize: new go.Size(6, 6), fill: "lightblue", stroke: "deepskyblue" }),
            $(go.Shape, { alignment: go.Spot.TopRight, cursor: "ne-resize", desiredSize: new go.Size(6, 6), fill: "lightblue", stroke: "deepskyblue" }),

            $(go.Shape, { alignment: go.Spot.Left, cursor: "w-resize", desiredSize: new go.Size(6, 6), fill: "lightblue", stroke: "deepskyblue" }),
            $(go.Shape, { alignment: go.Spot.Right, cursor: "e-resize", desiredSize: new go.Size(6, 6), fill: "lightblue", stroke: "deepskyblue" }),

            $(go.Shape, { alignment: go.Spot.BottomLeft, cursor: "se-resize", desiredSize: new go.Size(6, 6), fill: "lightblue", stroke: "deepskyblue" }),
            $(go.Shape, { alignment: go.Spot.Bottom, cursor: "s-resize", desiredSize: new go.Size(6, 6), fill: "lightblue", stroke: "deepskyblue" }),
            $(go.Shape, { alignment: go.Spot.BottomRight, cursor: "sw-resize", desiredSize: new go.Size(6, 6), fill: "lightblue", stroke: "deepskyblue" })
        );

    var nodeRotateAdornmentTemplate =
        $(go.Adornment,
            { locationSpot: go.Spot.Center, locationObjectName: "ELLIPSE" },
            $(go.Shape, "Ellipse", { name: "ELLIPSE", cursor: "pointer", desiredSize: new go.Size(7, 7), fill: "lightblue", stroke: "deepskyblue" }),
            $(go.Shape, { geometryString: "M3.5 7 L3.5 30", isGeometryPositioned: true, stroke: "deepskyblue", strokeWidth: 1.5, strokeDashArray: [4, 2] })
        );

    myDiagram.nodeTemplate =
        $(go.Node, "Spot",
            {
                locationSpot: go.Spot.Top,
                click: nodeClicked,
            },
            new go.Binding("location", "loc", go.Point.parse).makeTwoWay(go.Point.stringify),
            { selectable: true, selectionAdornmentTemplate: nodeSelectionAdornmentTemplate },
            { resizable: false, resizeObjectName: "PANEL", resizeAdornmentTemplate: nodeResizeAdornmentTemplate },
            { rotatable: false, rotateAdornmentTemplate: nodeRotateAdornmentTemplate },
            new go.Binding("angle").makeTwoWay(),
            // the main object is a Panel that surrounds a TextBlock with a Shape
            $(go.Panel, "Auto",
                { name: "PANEL" },
                new go.Binding("desiredSize", "size", go.Size.parse).makeTwoWay(go.Size.stringify),
                new go.Binding("customData").makeTwoWay(),
                $(go.Shape, "Rectangle",  // default figure
                    {
                        portId: "", // the default port: if no spot on link data, use closest side
                        fromLinkable: true, toLinkable: true, cursor: "pointer",
                        fill: "white",  // default color
                        strokeWidth: 1,
                        width: 70
                    },
                    new go.Binding("figure"),
                    new go.Binding("fill")),
                $(go.Panel, "Table",
                    { defaultAlignment: go.Spot.Left },
                    $(go.TextBlock,
                        {
                            font: "9pt Helvetica, Arial, sans-serif",
                            margin: 6,
                            maxSize: new go.Size(160, NaN),
                            editable: false,
                            row: 2, column: 0,
                            alignment: go.Spot.Center
                        },
                        new go.Binding("text").makeTwoWay()),
                    $(go.Picture,
                        {
                            row: 1, column: 0, margin: 6,
                            alignment: go.Spot.Center
                        },
                        new go.Binding("source").makeTwoWay())
                ),
            ),
            $(go.TextBlock,
                {
                    font: "9pt Helvetica, Arial, sans-serif",
                    editable: false,
                    alignment: go.Spot.Right, alignmentFocus: go.Spot.BottomLeft,
                },
                new go.Binding("text", "no_text"),
                new go.Binding("visible", "no_visible"),
            ),
            $(go.TextBlock,
                {
                    font: "9pt Helvetica, Arial, sans-serif",
                    editable: false,
                    alignment: go.Spot.Bottom, alignmentFocus: go.Spot.TopRight,
                },
                new go.Binding("text", "yes_text"),
                new go.Binding("visible", "yes_visible"),
            ),
            // four small named ports, one on each side:
            makePort("T", go.Spot.Top, false, true),
            makePort("L", go.Spot.Left, true, true),
            makePort("R", go.Spot.Right, true, true),
            makePort("B", go.Spot.Bottom, true, false),
            { // handle mouse enter/leave events to show/hide the ports
                mouseEnter: (e, node) => showSmallPorts(node, true),
                mouseLeave: (e, node) => showSmallPorts(node, false)
            }
        );

    function showSmallPorts(node, show) {
        node.ports.each(port => {
            if (port.portId !== "") {  // don't change the default port, which is the big shape
                port.fill = show ? "rgba(0,0,0,.3)" : null;
            }
        });
    }

    var linkSelectionAdornmentTemplate =
        $(go.Adornment, "Link",
            $(go.Shape,
                // isPanelMain declares that this Shape shares the Link.geometry
                { isPanelMain: true, fill: null, stroke: "deepskyblue", strokeWidth: 0 })  // use selection object's strokeWidth
        );

    function nodeClicked(e, obj) {  // executed by click and doubleclick handlers
        var evt = e.copy();
        var node = obj.part;
        var diagram_json = JSON.parse(myDiagram.model.toJson());
        var draganddropjson_for_data = JSON.parse(document.getElementById('draganddropjson_for_data').value);
        var emailbutton = document.getElementById("addEmailButton");
        var telegrambutton = document.getElementById("addTelegramButton");
        var delaybutton = document.getElementById("addDelayButton");
        var goalbutton = document.getElementById("addGoalButton");
        var triggerbutton = document.getElementById("addTriggerButton");
        switch (Object.keys(node.data.customData)[0]) {
            case "EMAIL_TEMPLATE":
                emailformreset();
                setbuttonattributes(diagram_json, emailbutton, node.data.key)
                set_data(draganddropjson_for_data, 'email', node.data.key)
                emailbutton.click();
                break;
            case "TELEGRAM":
                telegramformreset();
                setbuttonattributes(diagram_json, telegrambutton, node.data.key)
                set_data(draganddropjson_for_data, 'telegram', node.data.key)
                telegrambutton.click();
                break;
            case "DELAY":
                delayformreset();
                setbuttonattributes(diagram_json, delaybutton, node.data.key)
                set_data(draganddropjson_for_data, 'delay', node.data.key)
                delaybutton.click();
                break;
            case "GOAL":
                goalformreset();
                setbuttonattributes(diagram_json, goalbutton, node.data.key)
                set_data(draganddropjson_for_data, 'goal', node.data.key)
                goalbutton.click();
                break;

            case "TRIGGER":
                triggerformreset();
                setbuttonattributes(diagram_json, triggerbutton, node.data.key);
                set_data(draganddropjson_for_data, 'trigger', node.data.key)
                triggerbutton.click();
                break;
        }
    }

    myDiagram.linkTemplate =
        $(go.Link,  // the whole link panel
            { selectable: true, selectionAdornmentTemplate: linkSelectionAdornmentTemplate },
            { relinkableFrom: true, relinkableTo: true, reshapable: true },
            {
                routing: go.Link.AvoidsNodes,
                curve: go.Link.JumpOver,
                corner: 5,
                toShortLength: 4
            },
            new go.Binding("points").makeTwoWay(),
            $(go.Shape,  // the link path shape
                { isPanelMain: true, strokeWidth: 2 }),
            $(go.Shape,  // the arrowhead
                { toArrow: "Standard", stroke: null }),
            $(go.Panel, "Auto",
                new go.Binding("visible", "isSelected").ofObject(),
                $(go.Shape, "RoundedRectangle",  // the link shape
                    { fill: "#F8F8F8", stroke: null }),
                $(go.TextBlock,
                    {
                        textAlign: "center",
                        font: "6pt helvetica, arial, sans-serif",
                        margin: 2,
                        minSize: new go.Size(10, NaN),
                        editable: false
                    },
                    new go.Binding("text").makeTwoWay())
            )
        );

    go.Diagram.licenseKey = "...YourKeyHere...";

    load();  // load an initial diagram from some JSON text

    // initialize the Palette that is on the left side of the page
    myPalette =
        $(go.Palette, "myPaletteDiv",  // must name or refer to the DIV HTML element
            {
                maxSelectionCount: 1,
                nodeTemplateMap: myDiagram.nodeTemplateMap,  // share the templates used by myDiagram
                linkTemplate: // simplify the link template, just in this Palette
                    $(go.Link,
                        { // because the GridLayout.alignment is Location and the nodes have locationSpot == Spot.Center,
                            // to line up the Link in the same manner we have to pretend the Link has the same location spot
                            locationSpot: go.Spot.Center,
                            selectionAdornmentTemplate:
                                $(go.Adornment, "Link",
                                    { locationSpot: go.Spot.Center },
                                    $(go.Shape,
                                        { isPanelMain: true, fill: null, stroke: "deepskyblue", strokeWidth: 0 }),
                                    $(go.Shape,  // the arrowhead
                                        { toArrow: "Standard", stroke: null })
                                )
                        },
                        {
                            routing: go.Link.AvoidsNodes,
                            curve: go.Link.JumpOver,
                            corner: 5,
                            toShortLength: 4
                        },
                        new go.Binding("points"),
                        $(go.Shape,  // the link path shape
                            { isPanelMain: true, strokeWidth: 2 }),
                        $(go.Shape,  // the arrowhead
                            { toArrow: "Standard", stroke: null })
                    ),
                model: new go.GraphLinksModel([  // specify the contents of the Palette
                    { text: "Email", yes_text: "", no_text: "", yes_visible: false, no_visible: false, figure: "RoundedRectangle", customData: { EMAIL_TEMPLATE: '' }, source: "/static/main/img/email_icon.svg", fill: "#e1f1ff" },
                    { text: "Telegram", yes_text: "", no_text: "", yes_visible: false, no_visible: false, figure: "RoundedRectangle", customData: { TELEGRAM: '' }, source: "/static/main/img/telegram-logo.svg", fill: "#e1f1ff" },
                    { text: "Delay", yes_text: "", no_text: "", yes_visible: false, no_visible: false, figure: "RoundedRectangle", customData: { DELAY: '' }, source: "/static/main/img/clock.svg", fill: "#fbf1bd" },
                    { text: "Trigger", yes_text: "Yes", no_text: "No", yes_visible: true, no_visible: true, figure: "Diamond", customData: { TRIGGER: '' }, source: "/static/main/img/trigger.svg", fill: "#ffe1e1" },
                    { text: "Goal", yes_text: "", no_text: "", yes_visible: false, no_visible: false, figure: "RoundedRectangle", customData: { GOAL: '' }, source: "/static/main/img/goal.svg", fill: "#e6e0ff" },
                ])
            });
}


// Show the diagram's model in JSON format that the user may edit
function save(e, list_id) {
    e.preventDefault();
    var newsletter_form = document.getElementById('newsletter-form');
    const newsletter_name = document.getElementById(`newsletter_name${list_id}`);
    if (newsletter_name.value === '') {
        $("#newsletter-alert-name").show();
        setTimeout(function () {
            $("#newsletter-alert-name").hide();
        }, 10000);
    } else {
        result = draganddrop_check(e);
        if (result) {
            saveDiagramProperties();
            var diagram_json = JSON.parse(myDiagram.model.toJson());
            var draganddropjson = JSON.parse(document.getElementById(`draganddropjson`).value);
            var popups_data = JSON.parse(document.getElementById(`draganddropjson_for_data`).value);
            var data = { diagram: diagram_json, data: draganddropjson, popups_data: popups_data }
            document.getElementById(`draganddropjson`).value = JSON.stringify(data);
            newsletter_form.submit();

        }
    }
}
function load() {
    myDiagram.model = go.Model.fromJson(document.getElementById("mySavedModel").value);
    loadDiagramProperties();  // do this after the Model.modelData has been brought into memory
}

function saveDiagramProperties() {
    myDiagram.model.modelData.position = go.Point.stringify(myDiagram.position);
}
function loadDiagramProperties(e) {
    // set Diagram.initialPosition, not Diagram.position, to handle initialization side-effects
    var pos = myDiagram.model.modelData.position;
    if (pos) myDiagram.initialPosition = go.Point.parse(pos);
}
window.addEventListener('DOMContentLoaded', init);