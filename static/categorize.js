function categorize(theid, successFunction) {
  $("#button-" + theid).hide();
  var theValue = $('#item-' + theid).val();
  $.ajax({
         type: "POST",
         url: "/categorize",
         data: JSON.stringify({itemId: theid, thecategory: theValue}),
         success: function(data) {
           onItemCategorized(theid);
         },
         contentType: 'application/json; charset=utf-8'
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
