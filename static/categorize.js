var allcategoriesNames = [];

function insertCategories() {
  var theCatList = $("#catlist");
  theCatList.empty();
  for (var i = 0; i < allcategoriesNames.length; i++) {
    var newOption = $("<option>");
    newOption.val(allcategoriesNames[i]);
    theCatList.append(newOption);
  }
}

function deleteItem(theid) {
  $.ajax({
         type: "POST",
         url: "/deleteItem",
         data: JSON.stringify({itemId: theid}),
         success: function(data) {
           $('#entry-' + theid).hide();
         },
         contentType: "application/json; charset=utf-8"
       });

}

function updateItem(theid) {
  var thename = null;
  if ($('#name-' + theid).length != 0) {
    thename = $('#name-' + theid).val();
  }
  var thetitle = null;
  if ($('#title-' + theid).length != 0) {
    thetitle = $('#title-' + theid).val();
  }
  var theamount = null;
  if ($('#amount-' + theid).length != 0) {
    theamount = $('#amount-' + theid).val();
  }
  var theValue = $("#item-" + theid).val();
  var thenote = $("#note-" + theid).val();

  if (allcategoriesNames.indexOf(theValue) == -1) {
    allcategoriesNames.push(theValue);
    allcategoriesNames = allcategoriesNames.sort(function (a, b) {
      return a.toLowerCase().localeCompare(b.toLowerCase());
    }); // thats not very efficient.

    insertCategories();
  }

  $("#button-" + theid).addClass("dontshow");
  $.ajax({
         type: "POST",
         url: "/updateItem",
         data: JSON.stringify({itemId: theid, thecategory: theValue, thenote: thenote}),
         success: function(data) {
           if (theValue.trim() != "") {
             onItemCategorized(theid);
           }
         },
         contentType: "application/json; charset=utf-8"
       });
}

function isConfirmed(event, theid) {
  if (event !== false && event.keyCode == 13) {
    updateItem(theid);
    event.target.blur();
    return false;
  }

  $("#button-" + theid).removeClass("dontshow");
  return true;
}

function isConfirmedNewItem(event) {
  if (event !== false && event.keyCode == 13) {
    submitNewItem();
    event.target.blur();
    return false;
  }

  $("#button-newItemInput").removeClass("dontshow");
  return true;
}

function markEmptyFields(fieldIds) {
  var result = false;
  for (var i = 0; i < fieldIds.length; i++) {
    if ($("#" + fieldIds[i]).val() == null || $("#" + fieldIds[i]).val().trim() == "") {
      $("#" + fieldIds[i]).addClass("wrongInput");
      result = true;
    } else {
      $("#" + fieldIds[i]).removeClass("wrongInput");
    }
  }
  return result;
}

function submitNewItem() {
  var hasWrongInput = markEmptyFields(["newItemDate", "newItemName", "newItemDescription", "newItemAmount"]);
  if (isNaN($("#newItemAmount").val())) {
    $("#newItemAmount").addClass("wrongInput");
    hasWrongInput = true;
  }

  if (!hasWrongInput) {
    $.ajax({
           type: "POST",
           url: "/addNewItem",
           data: JSON.stringify({newItemDate: $("#newItemDate").val(),
                                 newItemName: $("#newItemName").val(),
                                 newItemDescription: $("#newItemDescription").val(),
                                 newItemAmount: $("#newItemAmount").val(),
                                 newItemCategory: $("#newItemCategory").val(),
                                 newItemNote: $("#newItemNote").val()
                               }),
           success: function(data) {
             if (data.errormsg == "") {
               $("#addRevenueInput").before(data.htmlentry);
               $("#newItemName").val("");
               $("#newItemDescription").val("");
               $("#newItemAmount").val("");
               $("#newItemCategory").val("");
               $("#newItemNote").val("");
             } else {
               window.alert(data.errormsg);
             }
           },
           dataType: "json",
           contentType: "application/json; charset=utf-8"
         });
   }
}


var detailsParams = {theX: null,
                     byCategory: "month",
                     fromDate: null,
                     toDate: null,
                     accounts: null,
                     patternInput: null,
                     categorySelection: null,
                     sortScatterBy: 'timestamp',
                     sortScatterByReverse: true
                    };

function doSortScatterBy(sortBy) {
  if (detailsParams["sortScatterBy"] == sortBy) {
    detailsParams["sortScatterByReverse"] = !detailsParams["sortScatterByReverse"];
  } else {
    detailsParams["sortScatterBy"] = sortBy;
    detailsParams["sortScatterByReverse"] = false;
  }
  showDetails(detailsParams);
}

function showDetails(params) {
  $("#details").html("<h2>Lade Details ...</h2>");
  $.ajax({
    type: "POST",
    url: "/getDetails",
    data: JSON.stringify({theX: params["theX"],
                          byCategory: params["byCategory"],
                          fromDate: params["fromDate"],
                          toDate: params["toDate"],
                          accounts: params["accounts"],
                          patternInput: params["patternInput"],
                          categorySelection: params["categorySelection"],
                          sortScatterBy: params["sortScatterBy"],
                          sortScatterByReverse: params["sortScatterByReverse"]}),
    success: function(thedata) {
      $("#details").html(thedata);
      insertCategories();
    },
    contentType: "application/json; charset=utf-8"
  });

}

function doDownload(params) {
  $.ajax({
    type: "POST",
    url: "/getDetails",
    data: JSON.stringify({theX: params["theX"],
                          byCategory: params["byCategory"],
                          fromDate: params["fromDate"],
                          toDate: params["toDate"],
                          accounts: params["accounts"],
                          patternInput: params["patternInput"],
                          categorySelection: params["categorySelection"],
                          sortScatterBy: params["sortScatterBy"],
                          sortScatterByReverse: params["sortScatterByReverse"],
                          csvexport: true}),
    success: function(thedata) {
        //var w = window.open("about:blank", "csvexport");
        //w.document.open();
        //w.document.write(thedata);
        //w.document.close();

        var newBlob = new Blob([thedata], {type: "text/csv; charset=utf-8"});
        var blobdata = window.URL.createObjectURL(newBlob);
        var thelink = document.createElement('a');
        thelink.href = blobdata;
        thelink.style.display = "none";
        thelink.download = "konto_" + params["fromDate"] + "_" + params["toDate"] + ".csv";
        $("body").append(thelink);
        thelink.click();
        setTimeout(function() {
            window.URL.revokeObjectURL(blobdata);
	    $(thelink).remove();
	}, 5000);

    },
    contentType: "application/json; charset=utf-8"
  });
}
