<!DOCTYPE html>

<html>
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>konto</title>
  <link rel="stylesheet" type="text/css" href="/static/css/style.css">
  <style>
    table {
      max-width: 100%;
      border-collapse: collapse;
      margin-top: 2em;
    }
    table tr:nth-child(odd){
      background-color: #f2f2f2;
    }
    table tr:hover:not(.error) {
      background-color: #ddd;
    }
  </style>
</head>
<body>

% if includeHeader == "showHeader":
  % include('menu.tpl', site=site)
% end

% for month, results in aggregatedDetails.items():
 <h2>{{month}}</h2>
 <div style="margin-left: 2em">
  <table style="white-space: pre;width: auto;margin-top: 1em">
   <caption>validation results</caption>
   <tr><th>rule/category</th><th>expected amount</th><th>current amount</th></tr>
  % for result in results["validatedRules"]:
   % if result["type"] == "warning":
    <tr style="background-color: #FFB6C1"><td>{{result["category"]}}</td><td>{{result["expected"]}}</td><td>{{result["current"]}}</td></tr>
   % else:
    <tr><td>{{result["category"]}}</td><td>{{result["expected"]}}</td><td>{{result["current"]}}</td></tr>
   % end
  % end
  </table>

 <table style="white-space: pre;width: auto;margin-top: 1em">
 <caption>transactions by category</caption>
 % for c in results["transactionsByCategory"]:
 <tr><td>{{c["category"]}}</td><td style="text-align:right">{{c["sum"]}}</td></tr>
 % end
 </table>

 <table style="white-space: pre;width: auto;margin-top: 1em">
 <caption>transactions by name</caption>
 % for c in results["transactionsByName"]:
 <tr><td>{{c["name"]}}</td><td style="text-align:right">{{c["sum"]}}</td></tr>
 % end
 </table>

 </div>
% end

% if includeHeader == "showHeader":
<p style="color: lightgray;margin-top: 3em;margin-left:1em">&copy; konto &mdash 2018-2020</p>
% end
</body>
</html>
