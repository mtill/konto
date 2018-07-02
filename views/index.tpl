<!DOCTYPE html>

% import datetime

% showDateSelector = byCategory != 'year'

<html>
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>konto - Übersicht</title>
  <link rel="stylesheet" type="text/css" href="/static/style.css">
  <script class="include" type="text/javascript" src="/static/jquery-3.3.1.min.js"></script>
  <script class="include" type="text/javascript" src="/static/categorize.js"></script>
  <script src="/static/plotly-latest.min.js"></script>
  <!-- <script src="https://cdn.plot.ly/plotly-latest.min.js"></script> -->

<script class="code" type="text/javascript">
var windowWidth = null;
var plotData = null;
detailsParams["byCategory"] = "{{byCategory}}";

function selectAllAccounts(clickedAccount) {
  var checkItems = !$(clickedAccount).prop("checked");
  $(".accountCheckbox").each(function() {
    if ($(this) != clickedAccount) {
      $(this).prop("checked", checkItems);
    }
  });
}

function storeDates() {
  % if showDateSelector:
  detailsParams["fromDate"] = $("#fromDate").val();
  detailsParams["toDate"] = $("#toDate").val();
  % end

  detailsParams["accounts"] = [];
  $(".accountCheckbox").each(function() {
    if ($(this).prop("checked")) {
      detailsParams["accounts"].push($(this).val());
    }
  });
  detailsParams["patternInput"] = $("#patternInput").val();
}

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

      detailsParams["theX"] = xPos;
      detailsParams["byCategory"] = "{{byCategory}}";

      showDetails(detailsParams);
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

  $('#duplicates').html("");
  $.ajax({
         type: "POST",
         url: "/getConsolidated",
         data: JSON.stringify({byCategory: "{{byCategory}}",
                               traces: {{! tracesJSON}},
                               fromDate: detailsParams["fromDate"],
                               toDate: detailsParams["toDate"],
                               accounts: detailsParams["accounts"],
                               patternInput: detailsParams["patternInput"]
                             }),
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

function refresh() {
  doPlot();
}

function submitSettingsForm() {
  storeDates();
  doPlot();
  showDetails(detailsParams);
  return false;
}

$(document).ready(function() {
  windowWidth=$(document).width();

  // $(window).resize(function(){
  //   if ($(document).width() != windowWidth) {
  //     doPlot();
  //   }
  // });

  storeDates();
  doPlot();

  % if byCategory == 'month':
  %   currentMonth = datetime.datetime.today().strftime('%Y-%m')
  detailsParams["theX"] = "{{currentMonth}}";
  showDetails(detailsParams);
  % end
});
</script>

</head>
<body>

% include('menu.tpl', site=site)

<fieldset style="margin-top: 0.5em">

  <form onsubmit="return submitSettingsForm()">
    <legend>Einstellungen</legend>
    <span style="margin-right: 2em">
      % for a in accounts:
      <input type="checkbox" class="accountCheckbox" ondblclick="selectAllAccounts($(this))" checked value="{{a}}">{{a}}
      % end
    </span>

    % if showDateSelector:
    %   fromDate = (datetime.datetime.today() - datetime.timedelta(days=5*30)).replace(day=1).strftime('%Y-%m-%d')
    %   toDate = datetime.datetime.today().strftime('%Y-%m-%d')
    von: <input type="date" id="fromDate" value="{{fromDate}}">
    bis: <input type="date" id="toDate" value="{{toDate}}">
    % end

    <span style="margin-left: 2em">Suche: <input type="text" id="patternInput" placeholder="Filter" value=""></span>
    <input type="submit" value="ok" style="margin-right:2em">

    <a href="javascript:doPlot()" style="font-size:10pt">Umsätze aktualisieren</a>
  </form>
</fieldset>

<div id="inout"></div>
<p id="duplicates"></p>
<p id="details"></p>

<p style="color: lightgray;margin-top: 3em;margin-left:1em">konto &mdash; &copy;<a href="https://github.com/mtill/konto" target="_blank" style="text-decoration:none;color: lightgray">Michael Till Beck</a>, 2018</p>
</body>
</html>
