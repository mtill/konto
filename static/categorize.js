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

function categorize(theid, successFunction) {
  var theValue = $("#item-" + theid).val();

  if (allcategoriesNames.indexOf(theValue) == -1) {
    allcategoriesNames.push(theValue);
    catlistValues = allcategoriesNames.sort(function (a, b) {
      return a.toLowerCase().localeCompare(b.toLowerCase());
    }); // thats not very efficient.

    insertCategories();
  }

  $("#button-" + theid).hide();
  $.ajax({
         type: "POST",
         url: "/categorize",
         data: JSON.stringify({itemId: theid, thecategory: theValue}),
         success: function(data) {
           $("#button-" + theid).hide();
           onItemCategorized(theid);
         },
         contentType: "application/json; charset=utf-8"
       });
}

function activateButton(theid) {
  var theItem = $("#item-" + theid);
  var theButton = $("#button-" + theid);
  if (theItem.attr("origValue") != theItem.val()) {
    theButton.show();
  } else {
    theButton.hide();
  }
}

function isEnter(event, theid) {
  if (event.keyCode == 13) {
    categorize(theid);
  }
}
