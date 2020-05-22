var detailsParams = {theX: null,
                     byCategory: "month",
                     fromDate: null,
                     toDate: null,
                     accounts: null,
                     patternInput: null,
                     categorySelection: null,
                     sortScatterBy: 'timestamp',
                     sortScatterByReverse: true,
                     minAmount: null,
                     maxAmount: null,
                     xfield: 'theX'
                    };


function getRequestJSON(params) {
  return {
    theX: params["theX"],
    xfield: params["xfield"],
    byCategory: params["byCategory"],
    fromDate: params["fromDate"],
    toDate: params["toDate"],
    accounts: params["accounts"],
    patternInput: params["patternInput"],
    categorySelection: params["categorySelection"],
    sortScatterBy: params["sortScatterBy"],
    sortScatterByReverse: params["sortScatterByReverse"],
    minAmount: params["minAmount"],
    maxAmount: params["maxAmount"]
  };
}

function showDetails(editable, msgtext, params) {
  editable.destroyTable();
  editable.showInitializingMessage(msgtext);
  fetch("/transactions/getDetails", {
    method: "POST",
    body: JSON.stringify(getRequestJSON(params)),
    headers: {
      "Content-Type": "application/json; charset=utf-8"
    }
  }).then(response => {
      if (!response.ok) { return response.text().then(m => {throw new Error(m); }) }
      return response.json();
  }).then(data => {
    editable.initializeTable(data["title"], data["data"]);
  }).catch(error => {
    editable.showInitializingMessage(msgtext + ": error.");
    window.alert(error);
  });
}

function doDownload(params) {
    let requestJSON = getRequestJSON(params);
    requestJSON["csvexport"] = true;
    fetch("/transactions/getDetails", {
      method: "POST",
      body: JSON.stringify(requestJSON),
      headers: {
        "Content-Type": "application/json; charset=utf-8"
      }
    }).then(response => {
        if (!response.ok) { return response.text().then(m => {throw new Error(m); }) }
        return response.blob();
    }).then(data => {
        let newBlob = new Blob([data], {type: "text/csv; charset=utf-8"});
        let blobdata = window.URL.createObjectURL(newBlob);
        let thelink = document.createElement('a');
        thelink.href = blobdata;
        thelink.style.display = "none";
        thelink.download = "konto_" + params["fromDate"] + "_" + params["toDate"] + ".csv";
        document.getElementsByTagName("body")[0].appendChild(thelink);
        thelink.click();
        setTimeout(function() {
            window.URL.revokeObjectURL(blobdata);
            document.getElementsByTagName("body")[0].removeChild(thelink);
        }, 5000);  
      }).catch(error => {
        window.alert(error);
      });

}
