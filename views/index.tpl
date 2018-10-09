<!DOCTYPE html>

% import datetime
% showDateSelector = True   #byCategory != 'year'
<html>
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>konto - Übersicht</title>
  <link rel="stylesheet" type="text/css" href="/static/style.css">
  <script class="include" type="text/javascript" src="/static/jquery-latest.min.js"></script>
  <script class="include" type="text/javascript" src="/static/categorize.js"></script>
  <script src="/static/plotly-latest.min.js"></script>
  <!-- <script src="https://cdn.plot.ly/plotly-latest.min.js"></script> -->

<script class="code" type="text/javascript">
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
  var wrongInput = false;

  var minAmount = $("#minAmount").val();
  if (minAmount.trim() == "") {
    minAmount = null;
  }
  var maxAmount = $("#maxAmount").val();
  if (maxAmount.trim() == "") {
    maxAmount = null;
  }

  if (minAmount != null && isNaN(minAmount)) {
    $("#minAmount").addClass("wrongInput");
    wrongInput = true;
  } else {
    minAmount = parseFloat(minAmount);
    $("#minAmount").removeClass("wrongInput");
  }

  if (maxAmount != null && isNaN(maxAmount)) {
    $("#maxAmount").addClass("wrongInput");
    wrongInput = true;
  } else {
    maxAmount = parseFloat(maxAmount);
    $("#maxAmount").removeClass("wrongInput");
  }

  if (wrongInput) {
    return false;
  }

  detailsParams["theX"] = null;

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

  detailsParams["minAmount"] = minAmount;
  detailsParams["maxAmount"] = maxAmount;

  return true;
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
                           barmode: "relative",
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
  $('#details').html("<h2 class=\"clickable\" onclick=\"showDetails(detailsParams)\">Umsätze <img src=\"/static/view-more.png\" alt=\"Details laden\">");
  //showDetails(detailsParams);
  $.ajax({
         type: "POST",
         url: "/getConsolidated",
         data: JSON.stringify({byCategory: "{{byCategory}}",
                               traces: {{! tracesJSON}},
                               fromDate: detailsParams["fromDate"],
                               toDate: detailsParams["toDate"],
                               accounts: detailsParams["accounts"],
                               patternInput: detailsParams["patternInput"],
                               minAmount: detailsParams["minAmount"],
                               maxAmount: detailsParams["maxAmount"]
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
  inoutPlot();
}

function submitSettingsForm() {
  var validInput = storeDates();
  if (validInput) {
    doPlot();
  }

  return false;
}

$(document).ready(function() {
  $(window).resize(function() {
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

<fieldset style="margin-top: 0.5em">

  <form onsubmit="return submitSettingsForm()">
    <legend>Einstellungen</legend>
    <span style="margin-right: 2em">
      % for a in accounts:
      <input type="checkbox" class="accountCheckbox" ondblclick="selectAllAccounts($(this))" checked value="{{a}}">{{a}}
      % end
    </span>

    % if showDateSelector:
    %   if byCategory == 'year':
    %     fromDate = '2000-01-01'
    %   else:
    %     fromDate = (datetime.datetime.today() - datetime.timedelta(days=5*30)).replace(day=1).strftime('%Y-%m-%d')
    %   end
    %   toDate = datetime.datetime.today().strftime('%Y-%m-%d')
    <span style="margin-left: 2em">Datum: <input type="date" id="fromDate" value="{{fromDate}}"> - <input type="date" id="toDate" value="{{toDate}}"></span>
    % end

    <span style="margin-left: 2em">Betrag: <input type="text" id="minAmount" size="5" placeholder="min" value=""> - <input type="text" id="maxAmount" size="5" placeholder="max" value=""></span>

    <span style="margin-left: 2em">Suche: <input type="text" size="10" id="patternInput" placeholder="Filter" value=""></span>

    <input type="submit" value="Umsätze anzeigen / aktualisieren" style="margin-left:2em">
  </form>
</fieldset>

<div style="min-width:400pt;width:100%" id="inout"></div>
<p id="duplicates"></p>
<p id="details"></p>

<p style="color: lightgray;margin-top: 3em;margin-left:1em">konto &mdash; &copy;<a href="https://github.com/mtill/konto" target="_blank" style="text-decoration:none;color: lightgray">Michael Till Beck</a>, 2018</p>
</body>
</html>
