var detailsParams = {theX: null,
                     groupBy: "month",
                     fromDate: null,
                     toDate: null,
                     accounts: null,
                     patternInput: null,
                     categorySelection: null,
                     sortScatterBy: 'timestamp',
                     sortScatterByReverse: true,
                     minAmount: null,
                     maxAmount: null,
                     barmode: "relative",
                     traces: ["traces", "profit"],
                     plotTitle: "debits and credits"
                    };


function showDetails(editable, transactionsByCategoryEditable, transactionsByNameEditable, params) {
  
  if (transactionsByCategoryEditable !== null) {
    transactionsByCategoryEditable.destroyTable();
    transactionsByCategoryEditable.showInitializingMessage("loading transactions by category ...");
  }
  if (transactionsByNameEditable !== null) {
    transactionsByNameEditable.destroyTable();
    transactionsByNameEditable.showInitializingMessage("loading transactions by name ...");
  }
  editable.destroyTable();
  editable.showInitializingMessage("loading details ...");
  
  fetch("/transactions/getDetails", {
    method: "POST",
    body: JSON.stringify(params),
    headers: {
      "Content-Type": "application/json; charset=utf-8"
    }
  }).then(response => {
      if (!response.ok) { return response.text().then(m => {throw new Error(m); }) }
      return response.json();
  }).then(data => {
    if (transactionsByCategoryEditable !== null) {
      transactionsByCategoryEditable.initializeTable("transactions by category " + data["title"] + " (not accumulated)", data["transactionsByCategory"]);
    }
    if (transactionsByNameEditable !== null) {
      transactionsByNameEditable.initializeTable("transactions by name " + data["title"] + " (not accumulated)", data["transactionsByName"]);
    }
    editable.initializeTable("transactions " + data["title"], data["data"]);
    }).catch(error => {
    editable.showInitializingMessage("error loading transactions.");
    if (transactionsByCategoryEditable !== null) {
      transactionsByCategoryEditable.showInitializingMessage("error loading transactions by category");
    }
    if (transactionsByNameEditable !== null) {
      transactionsByNameEditable.showInitializingMessage("error loading transactions by name.");
    }
    window.alert(error);
  });
}
