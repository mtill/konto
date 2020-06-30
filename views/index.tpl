<!DOCTYPE html>

% import datetime
% showDateSelector = True
<html>
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>konto</title>
  <link rel="stylesheet" type="text/css" href="/static/css/style.css">
  <link rel="stylesheet" type="text/css" href="/static/css/editable.css">
  <script class="include" type="text/javascript" src="/static/js/editable.js"></script>
  <script class="include" type="text/javascript" src="/static/js/categorize.js"></script>
  <!-- <script src="/static/js/plotly-latest.min.js"></script> -->
  <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>

  <style>
    #duplicates table tr td:nth-of-type(5) { font-family: monospace; text-align: right; }
    #details table tr td:nth-of-type(6) { font-family: monospace; text-align: right; }

    @media 
    only screen and (max-width: 760px),
    (min-device-width: 768px) and (max-device-width: 1024px)  {

      #details table thead tr.theadtr {
        display: none;
      }

      #details table, #details table tbody, #details table td:not(.hidden) {
        display: block;
      }

      #duplicates table tr td:nth-of-type(5) { text-align: left; }
      #details table tr td:nth-of-type(6) { text-align: left; }

      #details table tr td:nth-of-type(2):before { font-family: monospace; white-space: pre; content: "date:        "; }
      #details table tr td:nth-of-type(3):before { font-family: monospace; white-space: pre; content: "account:     "; }
      #details table tr td:nth-of-type(4):before { font-family: monospace; white-space: pre; content: "name:        "; }
      #details table tr td:nth-of-type(5):before { font-family: monospace; white-space: pre; content: "description: "; }
      #details table tr td:nth-of-type(6):before { font-family: monospace; white-space: pre; content: "amount:      "; }
      #details table tr td:nth-of-type(7):before { font-family: monospace; white-space: pre; content: "category:    "; }
      #details table tr td:nth-of-type(8):before { font-family: monospace; white-space: pre; content: "note:        "; }
    }
  </style>

<script class="code" type="text/javascript">
var duplicatesEditable = null;
var detailsEditable = null;
var transactionsByCategoryEditable = null;
var transactionsByNameEditable = null;

var plotData = null;

function selectAllAccounts(clickedAccount) {
  clickedAccount.checked = true;
  var q = document.querySelectorAll(".accountCheckbox");
  for (var i = 0; i < q.length; i++) {
    if (q[i] != clickedAccount) {
      q[i].checked = false;
    }
  }
}

function storeDates() {
  var wrongInput = false;

  var minAmount = document.getElementById("minAmount").value;
  if (minAmount.trim() == "") {
    minAmount = null;
  }
  var maxAmount = document.getElementById("maxAmount").value;
  if (maxAmount.trim() == "") {
    maxAmount = null;
  }

  if (minAmount != null && isNaN(minAmount)) {
    document.getElementById("minAmount").classList.add("wrongInput");
    wrongInput = true;
  } else {
    minAmount = parseFloat(minAmount);
    document.getElementById("minAmount").classList.remove("wrongInput");
  }

  if (maxAmount != null && isNaN(maxAmount)) {
    document.getElementById("maxAmount").classList.add("wrongInput");
    wrongInput = true;
  } else {
    maxAmount = parseFloat(maxAmount);
    document.getElementById("maxAmount").classList.remove("wrongInput");
  }

  if (wrongInput) {
    return false;
  }

  detailsParams["theX"] = null;

  % if showDateSelector:
  detailsParams["fromDate"] = document.getElementById("fromDate").value;
  detailsParams["toDate"] = document.getElementById("toDate").value;
  % end

  detailsParams["accounts"] = [];
  var q = document.querySelectorAll(".accountCheckbox");
  for (var i = 0; i < q.length; i++) {
    if (q[i].checked) {
      detailsParams["accounts"].push(q[i].value);
    }
  }
  detailsParams["patternInput"] = document.getElementById("patternInput").value;

  detailsParams["minAmount"] = minAmount;
  detailsParams["maxAmount"] = maxAmount;

  detailsParams["groupBy"] = document.getElementById("groupBy").value;

  if (document.getElementById("accumulated").checked) {
    detailsParams["traces"] = ['profit', 'profitaccumulated'];
    if (document.getElementById("classifyBy").value == "name") {
      detailsParams["traces"].push('nametracesaccumulated');
    } else if (document.getElementById("classifyBy").value == "category") {
      detailsParams["traces"].push('tracesaccumulated');
    }

    detailsParams["plotTitle"] = "accumulated debits and credits (starting from " + detailsParams["fromDate"] + ")";
  } else {
    detailsParams["traces"] = ['profit'];
    if (document.getElementById("classifyBy").value == "name") {
      detailsParams["traces"].push('nametraces');
    } else if (document.getElementById("classifyBy").value == "category") {
      detailsParams["traces"].push('traces');
    }

    detailsParams["plotTitle"] = "debits and credits";
  }

  detailsParams["barmode"] = "group";
  if (document.getElementById("barmode").checked) {
    detailsParams["barmode"] = "relative";
  }

  return true;
}

function inoutPlot() {
  if (plotData === null) {
    return;
  }
  traces = plotData["traces"];

  let dtick = "M1"; //M12

  inout = Plotly.newPlot("inout",
                         traces,
                         {title: detailsParams["plotTitle"],
                           //hovermode: "closest",
                           barmode: detailsParams["barmode"],
                           xaxis: {
                             // tick0: firstDate,
                             dtick: dtick
                           },
                           yaxis: {title: "Euro"},
                           legend: {traceorder: "normal"}
                          },
                          {
                            displaylogo: false
                          });

  document.getElementById("inout").on("plotly_click", function(eventdata) {
    for (var i=0; i < eventdata.points.length; i++) {
      var curveNumber = eventdata.points[i].curveNumber;
      var xPos = 0;
      if ("theX" in traces[curveNumber]) {
        xPos = traces[curveNumber]["theX"][eventdata.points[i].pointNumber];
      } else {
        xPos = traces[curveNumber]["x"][eventdata.points[i].pointNumber];
      }

      detailsParams["theX"] = xPos;

      showDetailsContainer();
      break;
    }
    // console.log(traces.points[i].curveNumber + "  "  + traces.points[i].pointNumber);
  });
}

function doPlot() {
  detailsEditable.destroyTable();
  duplicatesEditable.showInitializingMessage("loading duplicates ...");

  transactionsByCategoryEditable.destroyTable();
  transactionsByNameEditable.destroyTable();

  hideDetailsContainer();
  Plotly.purge("inout");
  document.getElementById("inout").innerText = "loading data ...";

  fetch("/getConsolidated", {
    method: "POST",
    body: JSON.stringify(detailsParams),
    headers: {
      "Content-Type": "application/json; charset=utf-8"
    }
  }).then(response => {
    if (!response.ok) { return response.text().then(m => {throw new Error(m); }) }
    return response.json();
  }).then(data => {
    document.getElementById("inout").innerText = "";
    plotData = data;
    duplicatesEditable.showInitializingMessage(null);
    if (plotData["foundDuplicates"].length != 0) {
      let duplicatesInitValues = [];
      for (let c of plotData["foundDuplicates"]) {
        duplicatesInitValues.push({"id":          c["id"],
                                   "date":        c['date'],
                                   "name":        c['name'],
                                   "description": c['description'],
                                   "amount":      c['amount'],
                                   "note":        c['note']});
      }
      duplicatesEditable.initializeTable("possible duplicates", duplicatesInitValues);
    }

    inoutPlot();
  }).catch(error => {
    document.getElementById("inout").innerText = "error loading data.";
    duplicatesEditable.showInitializingMessage("error loading duplicates.");
    window.alert(error);
  });

}

function refresh() {
  Plotly.purge("inout");
  inoutPlot();
}

function settingsFormInput(event) {
  if (event.keyCode == 13) {
    submitSettingsForm();
    return true;
  }
  return false;
}

function submitSettingsForm() {
  var validInput = storeDates();
  if (validInput) {
    doPlot();
  }

  return false;
}

function hideDetailsContainer() {
  document.getElementById('details').classList.add('hidden');
}

function showDetailsContainer() {
  document.getElementById('details').classList.remove('hidden');
  showDetails(detailsEditable, transactionsByCategoryEditable, transactionsByNameEditable, detailsParams)
}

function validateForm() {
  if (document.getElementById('accumulated').checked) {
    document.getElementById('barmode').disabled = true;
    document.getElementById('barmode').checked = false;
  } else {
    document.getElementById('barmode').disabled = false;
  }
}

document.addEventListener("DOMContentLoaded", function() {
  validateForm();

  let duplicatesKeyMap = new Map();
  duplicatesKeyMap.set("id",          {"type": "hidden",   "inputType": "text"});
  duplicatesKeyMap.set("date",        {"type": "readonly", "inputType": "date",   "additionalAttributes": {"required": "required"}});
  duplicatesKeyMap.set("name",        {"type": "readonly", "inputType": "text",   "additionalAttributes": {"size": "20"}});
  duplicatesKeyMap.set("description", {"type": "readonly", "inputType": "text",   "additionalAttributes": {"size": "50"}});
  duplicatesKeyMap.set("amount",      {"type": "readonly", "inputType": "number", "additionalAttributes": {"size": "6", "step": "0.1"}});
  duplicatesKeyMap.set("note",        {"type": "input",    "inputType": "text",   "additionalAttributes": {"size": "10"}});

  duplicatesEditable = new AjaxEditable({thenode:             document.getElementById("duplicates"),
                                         keyMap:              duplicatesKeyMap,
                                         errorkey:            "error",
                                         providedActions:     ["delete", "update"],
                                         sortable:            true,
                                         eidkey:              "id",
                                         baseURI:             "/transactions"});


  let keyMap = new Map();
  keyMap.set("id",          {"type": "hidden",   "inputType": "text"});
  keyMap.set("date",        {"type": "readonly", "inputType": "date",   "additionalAttributes": {"required": "required"}});
  keyMap.set("account",     {"type": "readonly", "inputType": "text",   "additionalAttributes": {"size": "4", "required": "required"}});
  keyMap.set("name",        {"type": "readonly", "inputType": "text",   "additionalAttributes": {"size": "20", "required": "required"}});
  keyMap.set("description", {"type": "readonly", "inputType": "text",   "additionalAttributes": {"size": "50", "required": "required"}});
  keyMap.set("amount",      {"type": "readonly", "inputType": "number", "additionalAttributes": {"step": "0.1", "size": "4", "required": "required"}});
  keyMap.set("category",    {"type": "input",    "inputType": "text",   "additionalAttributes": {"size": "10", "list": "categoriesNames"}});
  keyMap.set("note",        {"type": "input",    "inputType": "text",   "additionalAttributes": {"size": "10"}});

  detailsEditable = new AjaxEditable({thenode:             document.getElementById("details"),
                                      keyMap:              keyMap,
                                      errorkey:            "error",
                                      providedActions:     ["create", "update", "delete"],
                                      sortable:            true,
                                      eidkey:              "id",
                                      baseURI:             "/transactions"});

  let transactionsByCategoryKeyMap = new Map();
  transactionsByCategoryKeyMap.set("category",        {"type": "readonly", "inputType": "text",   "additionalAttributes": {"size": "20"}});
  transactionsByCategoryKeyMap.set("sum",             {"type": "readonly", "inputType": "number", "additionalAttributes": {"size": "6", "step": "0.1"}});
  transactionsByCategoryEditable = new Editable({thenode:  document.getElementById("details"),
                                      keyMap:              transactionsByCategoryKeyMap,
                                      errorkey:            "error",
                                      providedActions:     [],
                                      sortable:            true});

  let transactionsByNameKeyMap = new Map();
  transactionsByNameKeyMap.set("name",            {"type": "readonly", "inputType": "text",   "additionalAttributes": {"size": "20"}});
  transactionsByNameKeyMap.set("sum",             {"type": "readonly", "inputType": "number", "additionalAttributes": {"size": "6", "step": "0.1"}});
  transactionsByNameEditable = new Editable({thenode:      document.getElementById("details"),
                                      keyMap:              transactionsByNameKeyMap,
                                      errorkey:            "error",
                                      providedActions:     [],
                                      sortable:            true});


  window.addEventListener("resize", function() {
    refresh();
  });

  var validInput = storeDates();
  if (validInput) {
    doPlot();
  }
});
</script>

</head>
<body>

% include('menu.tpl', site=site)

<datalist id="categoriesNames">
 % for cat in categoriesNames:
  <option value="{{cat}}">
 % end
</datalist>

<fieldset style="margin-top: 0.5em">

  <form onsubmit="return submitSettingsForm()">
    <legend>settings</legend>

    <div>

      <span style="margin-right: 1em">
        % for a in accounts:
        <input type="checkbox" class="accountCheckbox" ondblclick="selectAllAccounts(this)" checked value="{{a}}">{{a}}
        % end
      </span>

      % if showDateSelector:
      %   fromDate = (datetime.datetime.today() - datetime.timedelta(days=5*30)).replace(day=1).strftime('%Y-%m-%d')
      %   toDate = datetime.datetime.today().strftime('%Y-%m-%d')
      <span style="margin-left: 1em">date: <input type="date" id="fromDate" value="{{fromDate}}"> - <input type="date" id="toDate" value="{{toDate}}"></span>
      % end

      <span style="margin-left: 1em">amount: <input type="text" id="minAmount" size="3" placeholder="min" value="" onkeyup="settingsFormInput(event)"> - <input type="text" id="maxAmount" size="3" placeholder="max" value="" onkeyup="settingsFormInput(event)"></span>

      <span style="margin-left: 1em">pattern: <input type="text" size="10" id="patternInput" placeholder="Filter" value="" onkeyup="settingsFormInput(event)"></span>

    </div><div>

      <span style="margin-left: 1em">classify by:
        <select name="classifyBy" id="classifyBy">
          <option value="category">category</option>
          <option value="name">name</option>
        </select>
      </span>

      <span style="margin-left: 1em">group by:
        <select name="groupBy" id="groupBy">
          <option value="week">week</option>
          <option value="month" selected>month</option>
          <option value="quarter">quarter</option>
          <option value="year">year</option>
        </select>
      </span>

      % if site != "sum":
      <span style="margin-left: 1em"><input id="barmode" type="checkbox" checked>stacked</span>
      % end

      <span style="margin-left: 1em"><input id="accumulated" type="checkbox" onchange="validateForm()">accumulated</span>

      <input type="submit" value="go" style="margin-left:1em">
    </div>

  </form>
</fieldset>

<div style="min-width:400pt;width:100%" id="inout"></div>
<p id="duplicates" class="scrollable"></p>

<h2>details <img src="/static/img/view-more.png" class="clickable" onclick="showDetailsContainer()" alt="Details laden"></h2>
<div id="details"></div>

<p style="color: lightgray;margin-top: 3em;margin-left:1em">&copy; konto &mdash 2018-2020</p>
</body>
</html>

