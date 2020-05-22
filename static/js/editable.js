class Editable {

    constructor({thenode, keyMap, errorkey, providedActions, sortable}) {
      this.thenode = thenode;
      this.keyMap = new Map();
      this.providedActions = providedActions;
      this.errorkey = errorkey;
      this.sortable = sortable;

      this.colToKey = {};
      this.sortInfo = null;
      for (const [keyk, keyv] of keyMap.entries()) {
        let klist = {};
        for (const [klk, klv] of Object.entries(keyv)) {
          klist[klk] = klv;
        }
        this.keyMap.set(keyk, klist);
      }
      this.thetable = null;
      this.thead = null;
      this.tbody = null;
      this.colToKey = null;
      this.msgnode = null;
    }

    destroyTable() {
      if (this.thetable !== null) {
        this.thenode.removeChild(this.thetable);
        this.thetable = null;
      }
      this.thead = null;
      this.tbody = null;
      this.showInitializingMessage(null);
    }

    showInitializingMessage(msgtext) {
      if (msgtext === null) {
        if (this.msgnode !== null) {
          this.thenode.removeChild(this.msgnode);
          this.msgnode = null;
        }
      } else {
        if (this.msgnode === null) {
          this.msgnode = document.createElement("div");
          this.thenode.appendChild(this.msgnode);
          this.msgnode.classList.add("initializingMessage");
        }
        this.msgnode.innerText = msgtext;
      }
    }

    initializeTable(title, entries) {
      let s = this;
      this.destroyTable();

      this.thetable = document.createElement("table");
      this.thenode.appendChild(this.thetable);
      this.thetable.classList.add("editable");

      if (title !== null) {
        let cap = document.createElement("caption");
        cap.innerText = title;
        this.thetable.appendChild(cap);
      }

      let thead = document.createElement("thead");
      this.thetable.appendChild(thead);
      let theadtr = document.createElement("tr");
      thead.appendChild(theadtr);
      theadtr.classList.add("theadtr");

      let colCount = 0;
      this.colToKey = {};
      for (let [keyk, keyv] of this.keyMap.entries()) {
        let theadth = document.createElement("th");
        theadtr.appendChild(theadth);
        theadth.innerText = keyk;
        if (keyv["type"] == "hidden") {
          theadth.classList.add("hidden");
        }
        if (this.sortable) {
          theadth.addEventListener("click", function() {s.sortTable(keyk);});
          theadth.classList.add("clickable");
        }
        keyv["th"] = theadth;
        this.colToKey[colCount] = keyk;
        colCount = colCount + 1;
      }

      if (this.providedActions.length != 0) {
        theadtr.appendChild(document.createElement("th")); // column with action links
      }

      this.thead = document.createElement("thead");
      this.thetable.appendChild(this.thead);

      this.tbody = document.createElement("tbody");
      this.thetable.appendChild(this.tbody);

      if (this.providedActions.includes("create")) {
        this._appendEntry(this.thead, null, "afterbegin");
      }
      for (let e of entries) {
        this._appendEntry(this.tbody, e, "beforeend");
      }
    }

    /*acceptAllModifications() {
      for (const ee of this.tbody.querySelectorAll('.modified')) {
        ee.classList.remove("modified");
      }
    }*/

    sortTable(thekey) {
      //let startDate = new Date().getTime();
      let doReverse = false;
      if (this.sortInfo !== null) {
        let k = this.sortInfo["key"];
        if (k == thekey) {
          doReverse = !this.sortInfo["reverse"];
        } else {
          this.keyMap.get(k)["th"].innerText = k;
        }
      }
      this.sortInfo = {"key": thekey, "reverse": doReverse};
      let symb = "↓";
      if (doReverse) {
        symb = "↑";
      }
      this.keyMap.get(thekey)["th"].innerText = thekey + symb;

      /*let entries = this.parseTable();
      if (doReverse) {
        entries.reverse(function(a, b) {
          return a[thekey].localeCompare(b[thekey]);
        });
      } else {
        entries.sort(function(a, b) {
          return a[thekey].localeCompare(b[thekey]);
        });
      }

      this.destroyTable();
      this.initializeTable(title, entries);*/

      let s = this;
      let comp = function(a, b) {
        return s.parseRow(a, false, false)[thekey].localeCompare(s.parseRow(b, false, false)[thekey]);
      }
      let appen = function(ele) {
        s.tbody.appendChild(ele);
      }
      if (doReverse) {
        Array.from(s.tbody.children).reverse(comp).forEach(appen);
      } else {
        Array.from(s.tbody.children).sort(comp).forEach(appen);
      }

      //console.log(new Date().getTime() - startDate);
    }

    _appendEntry(appendToNode, entryJSON, insertPosition) {
      let s = this;
      let ttr = document.createElement("tr");
      appendToNode.insertAdjacentElement(insertPosition, ttr);
      if (entryJSON === null) {
        ttr.classList.add("ignoreexport");
      } else {
        if (entryJSON.hasOwnProperty(this.errorkey) && entryJSON[this.errorkey] !== null) {
          ttr.classList.add("error");
          ttr.setAttribute("title", entryJSON[this.errorkey]);
        }
      }

      for (let [keyk, keyv] of this.keyMap.entries()) {
        let v = "";
        if (entryJSON !== null && entryJSON[keyk] !== null) {
          v = entryJSON[keyk];
        }
        let td = document.createElement("td");
        ttr.appendChild(td);

        if ((keyv["type"] != "hidden" && entryJSON === null) || keyv["type"] == "input") {
          let theinput = document.createElement("input");
          theinput.setAttribute("type", keyv["inputType"]);
          if (keyv.hasOwnProperty("additionalAttributes")) {
            for (const [ak, av] of Object.entries(keyv["additionalAttributes"])) {
              theinput.setAttribute(ak, av);
            }
          }
          theinput.setAttribute("value", v);
          td.appendChild(theinput);
          td.getCellValue = function() {
            if (!theinput.checkValidity()) {
              return null;
            }
            return theinput.value;
          }
          td.setCellValue = function(v) {
            theinput.value = v;
          }

          theinput.addEventListener("input", function(event) {
            if (!td.classList.contains("modified")) {
              td.classList.add("modified");
            }
            if (!ttr.classList.contains("modified")) {
              ttr.classList.add("modified");
            }
          });

        } else {
          td.innerText = v;

          if (keyv["type"] == "hidden") {
            td.classList.add("hidden");
          }
          if (keyv["type"] == "editable" || entryJSON === null) {
            td.setAttribute("contenteditable", "true");
            td.addEventListener("input", function(event) {
              if (!td.classList.contains("modified")) {
                td.classList.add("modified");
              }
              if (!ttr.classList.contains("modified")) {
                ttr.classList.add("modified");
              }
            });
  
          }
          td.getCellValue = function() {
            return td.innerText;
          }
          td.setCellValue = function(v) {
            td.innerText = v;
          }
        }
      }

      if (this.providedActions.length != 0) {
        let actiontd = document.createElement("td");
        ttr.appendChild(actiontd);
        actiontd.classList.add("actions");
        actiontd.classList.add("ignoreexport");

        if (this.providedActions.includes("update")) {
          let submitChanges = document.createElement("img");
          submitChanges.classList.add("clickable");
          submitChanges.classList.add("showWhenModified");
          actiontd.appendChild(submitChanges);
          if (entryJSON === null) {
            submitChanges.addEventListener("click", function() {
              let p = s.parseRow(ttr, true, true);
              if (p === null) {
                window.alert("some fields contain invalid input");
              } else {
                s.appendEntry(p, "afterbegin");
                s.markAsUnmodified(ttr);
              }
            });
          } else {
            submitChanges.addEventListener("click", function() {
              s.updateEntry(ttr);
            });
          }
          submitChanges.src = "/static/img/ok.png";
        }

        if (this.providedActions.includes("delete") && entryJSON !== null) {
          let removespan = document.createElement("img");
          removespan.classList.add("clickable");
          actiontd.appendChild(removespan);
          removespan.addEventListener("click", function() {s.removeEntry(this.parentNode.parentNode);});
          removespan.src = "/static/img/delete.png";
        }

        /*let upspan = document.createElement("img");
        upspan.classList.add("clickable");
        actiontd.appendChild(upspan);
        upspan.addEventListener("click", function() {s.tableUp(this);});
        upspan.src = "/static/img/up.png";

        let downspan = document.createElement("img");
        downspan.classList.add("clickable");
        actiontd.appendChild(downspan);
        downspan.addEventListener("click", function() {s.tableDown(this);});
        downspan.src = "/static/img/down.png";*/
      }
    }

    appendEntry(entryJSON, insertPosition) {
      this._appendEntry(this.tbody, entryJSON, insertPosition);
    }

    markAsUnmodified(tre) {
      for (const ee of tre.querySelectorAll('td')) {
        ee.classList.remove("modified");
      }
      tre.classList.remove("modified");
    }

    updateEntry(tre) {
      this.markAsUnmodified(tre);
    }

    removeEntry(tre) {
      tre.parentNode.removeChild(tre);
    }

    /*
    tableUp(e) {
      let row = e.parentNode.parentNode; // tr
      let prev = row.previousElementSibling;
      if (prev !== null && prev.tagName.toLowerCase() == "tr") {
        prev.before(row);
        if (!row.classList.contains("modified")) {
          row.classList.add("modified");
        }
      }
    }

    tableDown(e) {
      let row = e.parentNode.parentNode; // tr
      let next = row.nextElementSibling;
      if (next !== null && next.tagName.toLowerCase() == "tr") {
        next.after(row);
        if (!row.classList.contains("modified")) {
          row.classList.add("modified");
        }
      }
    }*/

    parseRow(tre, clearContent, checkValidity) {
      let h = {};
      let colCount = 0;
      if (checkValidity) {
        for (const ee of tre.querySelectorAll('td')) {
          if (!ee.classList.contains("ignoreexport")) {
            let v = ee.getCellValue();
            if (v === null) {
              return null;
            }
          }
        }
      }
      for (const ee of tre.querySelectorAll('td')) {
        if (!ee.classList.contains("ignoreexport")) {
          h[this.colToKey[colCount]] = ee.getCellValue();
          if (clearContent) {
            ee.setCellValue("");
          }
        }
        colCount = colCount + 1;
      }
      return h;
    }

    parseTable() {
      let rows = this.tbody.querySelectorAll('tr');
      let data = [];
      let s = this;
      rows.forEach(function(tre) {
        if (!tre.classList.contains("ignoreexport")) {
          data.push(s.parseRow(tre, false, false));
        }
      });

      //document.getElementById("jsoncontent").value = JSON.stringify(data);
      return data;
    }

}


class AjaxEditable extends Editable {
  constructor({thenode, keyMap, errorkey, providedActions, eidkey, sortable, baseURI=""}) {
    super({thenode: thenode, keyMap: keyMap, errorkey: errorkey, providedActions: providedActions, sortable: sortable});
    this.baseURI = baseURI;
    this.eidkey = eidkey;
  }

  appendEntry(entryJSON, insertPosition) {
    if (entryJSON === null) {
      super.appendEntry(null, insertPosition);
    } else {
      fetch(this.baseURI + "/createEntry", {
        method: "POST",
        body: JSON.stringify({"entry": entryJSON}),
        headers: {
          "Content-Type": "application/json; charset=utf-8"
        }
      }).then(response => {
        if (!response.ok) { return response.text().then(m => {throw new Error(m); }) }
        return response.json();
      }).then(data => {
        entryJSON[this.eidkey] = data.eid;
        super.appendEntry(entryJSON, insertPosition);
      }).catch(error => {
        window.alert(error);
      });
    }
  }

  updateEntry(tre) {
    let treJSON = this.parseRow(tre, false, true);
    if (treJSON !== null) {
      let theid = treJSON[this.eidkey];
      delete treJSON[this.eidkey];

      if (theid == "") {
        window.alert("missing id");
      } else {
        fetch(this.baseURI + "/updateEntry/" + theid, {
          method: "POST",
          body: JSON.stringify({"entry": treJSON}),
          headers: {
            "Content-Type": "application/json; charset=utf-8"
          }
        }).then(response => {
          if (!response.ok) { return response.text().then(m => {throw new Error(m); }) }
          super.updateEntry(tre);
        }).catch(error => {
          window.alert(error);
        });
      }
    }
  }

  removeEntry(tre) {
    let treJSON = this.parseRow(tre, false, false);
    if (confirm("Are you sure you'd like to delete this item?")) {
      let theid = treJSON[this.eidkey];
      fetch(this.baseURI + "/deleteEntry/" + theid, {
        method: "GET",
        headers: {
          "Content-Type": "application/json; charset=utf-8"
        }
      }).then(response => {
        if (!response.ok) { return response.text().then(m => {throw new Error(m); }) }
        super.removeEntry(tre);
      }).catch(error => {
        window.alert(error);
      });
    }
  }

}
