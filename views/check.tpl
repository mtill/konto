<!DOCTYPE html>

<html>
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>konto</title>
  <link rel="stylesheet" type="text/css" href="/static/css/style.css">
</head>
<body>

% if includeHeader == "showHeader":
  % include('menu.tpl', site=site)
% end

% for month, results in months.items():
 <h2>{{month}}</h2>
 <div style="margin-left: 2em">
  <p style="font-weight: bold">Gewinn: {{profitOverview[month]}}</p>

  <table style="white-space: pre;width: auto;margin-top: 1em">
   <caption>rules</caption>
   <tr><th>rule/category</th><th>debit</th><th>actual value</th></tr>
  % for result in results:
   % if result["type"] == "warning":
    <tr style="background-color: #FFB6C1"><td>{{result["category"]}}</td><td>{{result["expected"]}}</td><td>{{result["current"]}}</td></tr>
   % else:
    <tr><td>{{result["category"]}}</td><td>{{result["expected"]}}</td><td>{{result["current"]}}</td></tr>
   % end
  % end
  </table>

 <table style="white-space: pre;width: auto;margin-top: 1em">
 <caption>by category</caption>
 % for c in categoryOverview[month]:
 <tr><td>{{c["category"]}}</td><td style="text-align:right">{{c["sum"]}}</td></tr>
 % end
 </table>

 <table style="white-space: pre;width: auto;margin-top: 1em">
 <caption>by name</caption>
 % for c in transactionsByNameOverview[month]:
 <tr><td>{{c["name"]}}</td><td style="text-align:right">{{c["sum"]}}</td></tr>
 % end
 </table>

 </div>
% end

% if includeHeader == "showHeader":
<p style="color: lightgray;margin-top: 3em;margin-left:1em">konto &mdash; &copy;<a href="https://github.com/mtill/konto" target="_blank" style="text-decoration:none;color: lightgray">Michael Till Beck</a>, 2018-2020</p>
% end
</body>
</html>
