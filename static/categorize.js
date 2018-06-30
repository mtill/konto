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

function updateItem(theid) {
  var thename = null;
  if ($('#name-' + theid).length == 1) {
    thename = $('#name-' + theid).val();
  }
  var thetitle = null;
  if ($('#title-' + theid).length == 1) {
    thename = $('#title-' + theid).val();
  }
  var theamount = null;
  if ($('#amount-' + theid).length == 1) {
    thename = $('#amount-' + theid).val();
  }
  var theValue = $("#item-" + theid).val();
  var thedescription = $("#description-" + theid).val();

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
         data: JSON.stringify({itemId: theid, thecategory: theValue, thedescription: thedescription}),
         success: function(data) {
           if (theValue.trim() != "") {
             onItemCategorized(theid);
           }
         },
         contentType: "application/json; charset=utf-8"
       });
}

function isConfirmed(event, theid) {
  if (event.keyCode == 13) {
    updateItem(theid);
    event.target.blur();
    return false;
  }

  $("#button-" + theid).removeClass("dontshow");
  return true;
}

function isConfirmedNewItem(event) {
  if (event.keyCode == 13) {
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
  var hasWrongInput = markEmptyFields(["newItemDate", "newItemName", "newItemTitle", "newItemAmount"]);
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
                                 newItemTitle: $("#newItemTitle").val(),
                                 newItemAmount: $("#newItemAmount").val(),
                                 newItemCategory: $("#newItemCategory").val(),
                                 newItemDescription: $("#newItemDescription").val()
                               }),
           success: function(data) {
             if (data.errormsg == "") {
               $("#addRevenueInput").before(data.htmlentry);
               $("#newItemName").val("");
               $("#newItemTitle").val("");
               $("#newItemAmount").val("");
               $("#newItemCategory").val("");
               $("#newItemDescription").val("");
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
                     sortScatterBy: 'date',
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

function showDetails(params, action=null, actionParam=null) {
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
                          sortScatterByReverse: params["sortScatterByReverse"],
                          action: action,
                          actionParam: actionParam}),
    success: function(thedata) {
      $("#details").html(thedata);
      insertCategories();
    },
    contentType: "application/json; charset=utf-8"
  });
}
