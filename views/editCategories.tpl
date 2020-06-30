<!DOCTYPE html>

<html>
 <head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>konto</title>
  <link rel="stylesheet" type="text/css" href="/static/css/style.css">
  <link rel="stylesheet" type="text/css" href="/static/css/editable.css" />
  <script class="include" type="text/javascript" src="/static/js/categorize.js"></script>
  <script src="/static/js/editable.js"></script>

  <script type="text/javascript">
    var categoriesEditable = null;
    var detailsEditable = null;

    document.addEventListener("DOMContentLoaded", function() {
      let categoriesKeyMap = new Map();
      categoriesKeyMap.set("id",             {"type": "hidden", "inputType": "text"});
      categoriesKeyMap.set("category",       {"type": "input",  "inputType": "text",   "additionalAttributes": {"size": "20", "list": "categoriesNames", "required": "required"}});
      categoriesKeyMap.set("field",          {"type": "input",  "inputType": "text",   "additionalAttributes": {"size": "10", "required": "required"}});
      categoriesKeyMap.set("pattern",        {"type": "input",  "inputType": "text",   "additionalAttributes": {"size": "50", "required": "required"}});
      categoriesKeyMap.set("expectedValue",  {"type": "input",  "inputType": "number", "additionalAttributes": {"size": "6", "step": "0.1"}});
      categoriesKeyMap.set("priority",       {"type": "input",  "inputType": "number", "additionalAttributes": {"size": "3"}});

      let initialEntries = [];
      % for e in categories:
        % ev = "" if e["expectedValue"] is None else e["expectedValue"]
      initialEntries.push({"id":            "{{e["id"]}}",
                           "category":      "{{e["category"]}}",
                           "field":         "{{e["field"]}}",
                           "pattern":       "{{e["pattern"]}}",
                           "expectedValue": "{{ev}}",
                           "priority":      "{{e["priority"]}}"});
      % end

      categoriesEditable = new AjaxEditable({thenode:             document.getElementById("categories"),
                                             keyMap:              categoriesKeyMap,
                                             errorkey:            "error",
                                             providedActions:     ["create", "update", "delete"],
                                             sortable:            true,
                                             eidkey:              "id",
                                             baseURI:             "/categories"});
      categoriesEditable.initializeTable("un-categorized entries (excerpt)", initialEntries);


      let detailsKeyMap = new Map();
      detailsKeyMap.set("id",          {"type": "hidden",   "inputType": "text"});
      detailsKeyMap.set("date",        {"type": "readonly", "inputType": "text",   "additionalAttributes": {"required": "required"}});
      detailsKeyMap.set("account",     {"type": "readonly", "inputType": "text",   "additionalAttributes": {"size": "4", "required": "required"}});
      detailsKeyMap.set("name",        {"type": "readonly", "inputType": "text",   "additionalAttributes": {"size": "10", "required": "required"}});
      detailsKeyMap.set("description", {"type": "readonly", "inputType": "text",   "additionalAttributes": {"size": "10", "required": "required"}});
      detailsKeyMap.set("amount",      {"type": "readonly", "inputType": "number", "additionalAttributes": {"size": "6", "step": "0.1", "required": "required"}});
      detailsKeyMap.set("category",    {"type": "input",    "inputType": "text",   "additionalAttributes": {"size": "10", "list": "categoriesNames"}});
      detailsKeyMap.set("note",        {"type": "input",    "inputType": "text",   "additionalAttributes": {"size": "10"}});

      detailsEditable = new AjaxEditable({thenode:              document.getElementById("details"),
                                          keyMap:               detailsKeyMap,
                                          errorkey:             "error",
                                          providedActions:      ["update", "delete"],
                                          sortable:             true,
                                          eidkey:               "id",
                                          baseURI:              "/transactions"});


      detailsParams["categorySelection"] = ["not categorized"];
      detailsParams["fromDate"] = "{{fromDate}}";
      detailsParams["toDate"] = "{{toDate}}";
      showDetails(detailsEditable, null, null, detailsParams)
    });

  </script>
 </head>
 <body>

% include('menu.tpl', site='editCategories')

  <datalist id="categoriesNames">
  % for cat in categoriesNames:
    <option value="{{cat}}">
  % end
  </datalist>

  <h2>categories</h2>
  <div id="categories" class="scrollable"></div>
  <hr>

  <h2>un-categorized transactions (excerpt)</h2>
  <div id="details" style="margin-top:2em" class="scrollable"></div>

  <p style="color: lightgray;margin-top: 3em;margin-left:1em">&copy; konto &mdash 2018-2020</p>
 </body>
</html>

