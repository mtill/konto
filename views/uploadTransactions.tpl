<!DOCTYPE html>

<html>
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>konto</title>
  <link rel="stylesheet" type="text/css" href="/static/css/style.css" />
  <link rel="stylesheet" type="text/css" href="/static/css/editable.css" />

  <script src="/static/js/editable.js"></script>
  <script>
    var editable = null;

    function doUpload() {
      var entries = editable.parseTable();

      fetch("/uploadTransactions", {
        method: "POST",
        body: JSON.stringify({
          entries: entries, account: "{{account}}"
        }),
        headers: {
          "Content-Type": "application/json; charset=utf-8"
        }
      }).then(response => {
        if (!response.ok) { return response.text().then(m => {throw new Error(m); }) }
        return response.text();
      }).then(data => {
        var t = document.getElementById("firstpage");
        t.parentNode.removeChild(t);
        document.getElementById("secondpage").innerHTML = data;
      }).catch(error => {
        window.alert(error);
      });


    }

    document.addEventListener("DOMContentLoaded", function() {
      let keyMap = new Map();
      keyMap.set("date",        {"type": "editable", "inputType": "date",   "additionalAttributes": {"required": "required"}});
      keyMap.set("name",        {"type": "editable", "inputType": "text",   "additionalAttributes": {"size": "10", "required": "required"}});
      keyMap.set("description", {"type": "editable", "inputType": "text",   "additionalAttributes": {"size": "10", "required": "required"}});
      keyMap.set("amount",      {"type": "editable", "inputType": "number", "additionalAttributes": {"size": "4", "step": "0.1", "required": "required"}});

      editable = new Editable({thenode:             document.getElementById("tablediv"),
                               keyMap:              keyMap,
                               errorkey:            "error",
                               providedActions:     ["update", "delete"],
                               sortable:            true});
      let initValues = [];
      % for c in content:
      initValues.push({"date": "{{c['date']}}",
                       "name": "{{c['name']}}",
                       "description": "{{c['description']}}",
                       "amount": "{{c['amount']}}",
        % if c['error'] is None:
                       "error": null
        % else:
                       "error": "{{c['error']}}"
        % end
                      });
      %end
      editable.initializeTable(null, initValues);
      
    });
 </script>

 </head>
<body>

% include('menu.tpl', site=site)

<div id="firstpage">
  <div id="tablediv"></div>

  <input type="button" value="import entries" onclick="doUpload()">
</div>

<div id="secondpage"></div>

<p style="color: lightgray;margin-top: 3em;margin-left:1em">konto &mdash; &copy;<a href="https://github.com/mtill/konto" target="_blank" style="text-decoration:none;color: lightgray">Michael Till Beck</a>, 2018-2020</p>
</body>
</html>
