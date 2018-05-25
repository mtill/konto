<!DOCTYPE html>

% import datetime

% showDateSelector = byCategory != 'year'

<html>
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <title>konto - Übersicht</title>
  <link rel="stylesheet" type="text/css" href="/static/style.css">
  <script class="include" type="text/javascript" src="/static/jquery-3.3.1.min.js"></script>
  <script class="include" type="text/javascript" src="/static/categorize.js"></script>
  <script src="/static/plotly-latest.min.js"></script>
  <!-- <script src="https://cdn.plot.ly/plotly-latest.min.js"></script> -->

<script class="code" type="text/javascript">
var windowWidth = null;
var plotData = null;

% if showDateSelector:
var fromDate = null;
var toDate = null;

function storeDates() {
  fromDate = $("#fromDate").val();
  toDate = $("#toDate").val();
}
% end

function onItemCategorized(theid) {
  // doPlot();
}

function inoutPlot() {
  traces = plotData["traces"];
  Plotly.purge("inout")

  % if byCategory == 'year':
  %   dtick = 'M12'
  % else:
  %   dtick = 'M1'
  % end

//  var firstDate = traces[0]['x'][0];
//  for (var i = 1; i < traces.length; i++) {
//    if (firstDate > traces[i]['x'][0]) {
//      firstDate = traces[i]['x'][0];
//    }
//  }
//  firstDate = firstDate + "-01"

  //inout = temperature.sort(function(a,b) {return a.name.localeCompare(b.name)});
  //inout = Plotly.newPlot("temperature", temperature, {title: "Temperatur", xaxis: {range:[theDate+" 00:00:00", theDate+" 23:59:59"]}, yaxis: {title: "Temperatur [°C]"}}, {displaylogo: false});
  inout = Plotly.newPlot("inout",
                         traces,
                         {title: "{{title}}",
                           //hovermode: "closest",
                           barmode: "stack",
                           xaxis: {
                             // tick0: firstDate,
                             dtick: "{{dtick}}"
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

      showDetails(xPos);
      break;
    }
    // console.log(traces.points[i].curveNumber + "  "  + traces.points[i].pointNumber);
  });
}

function doPlot() {
  //var items = new Array();
  //$('#filesSelect option:selected').each(function() {
  //  items.push($(this).val());
  //});

  $('#duplicates').html("").hide();
  $.ajax({
         type: "POST",
         url: "/getConsolidated",
         % if showDateSelector:
         data: JSON.stringify({byCategory: "{{byCategory}}", traces: {{! tracesJSON}}, fromDate: fromDate, toDate: toDate}),
         % else:
         data: JSON.stringify({byCategory: "{{byCategory}}", traces: {{! tracesJSON}}}),
         % end
         success: function(thedata) {
           plotData = thedata;
           if (plotData["foundDuplicates"].length != 0) {
             $("#duplicates").html("<h2>Mögliche Duplikate gefunden:</h2>\n" + plotData["foundDuplicates"].join('<br>\n')).show();
           }
           inoutPlot();
         },
         dataType: "json",
         contentType: "application/json; charset=utf-8"
       });
}

function showDetails(theX) {
  $("#details").html("");
  $.ajax({
    type: "POST",
    url: "/getDetails",
    % if showDateSelector:
    data: JSON.stringify({theX: theX, byCategory: "{{byCategory}}", traces: ['scatter'], fromDate: fromDate, toDate: toDate}),
    % else:
    data: JSON.stringify({theX: theX, byCategory: "{{byCategory}}", traces: ['scatter']}),
    % end
    success: function(thedata) {
      $("#details").html(thedata);
      insertCategories();
    },
    contentType: "application/json; charset=utf-8"
  });
}

function refresh() {
  doPlot();
}

$(document).ready(function() {
  windowWidth=$(document).width();

  // $(window).resize(function(){
  //   if ($(document).width() != windowWidth) {
  //     doPlot();
  //   }
  // });

  % if showDateSelector:
  storeDates();
  % end
  doPlot();

  % if byCategory == 'month':
  %   currentMonth = datetime.datetime.today().strftime('%Y-%m')
  showDetails("{{currentMonth}}")
  % end
});
</script>

</head>
<body>

% include('menu.tpl', site=site)

% if showDateSelector:
%   fromDate = (datetime.datetime.today() - datetime.timedelta(days=5*30)).replace(day=1).strftime('%Y-%m-%d')
%   toDate = datetime.datetime.today().strftime('%Y-%m-%d')
von: <input type="date" id="fromDate" value="{{fromDate}}">
bis: <input type="date" id="toDate" value="{{toDate}}">
<input type="button" value="ok" onclick="storeDates(); doPlot()" style="margin-right:2em">
% end

<a href="javascript:doPlot()" style="font-size:10pt">Umsätze aktualisieren</a>
<div id="inout"></div>
<p id="duplicates"></p>
<p id="details"></p>

<p style="color: lightgray;margin-top: 3em;margin-left:1em">konto &mdash; &copy;<a href="https://github.com/mtill/konto" target="_blank" style="text-decoration:none;color: lightgray">Michael Till Beck</a>, 2018</p>
</body>
</html>
