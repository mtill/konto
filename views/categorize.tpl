<h2>{{title}}</h2>

% import json

<datalist id="catlist">
</datalist>

<script class="code" type="text/javascript">
  allcategoriesNames = {{! json.dumps(allcategoriesNames)}};
</script>

<div style="overflow-x:auto">
<table>
  <thead>
    <tr>
      <th class="clickable" onclick="doSortScatterBy('date')">Datum</th>
      <th class="clickable" onclick="doSortScatterBy('name')">Name</th>
      <th class="clickable" onclick="doSortScatterBy('description')">Beschreibung</th>
      <th class="clickable" onclick="doSortScatterBy('amount')">Betrag</th>
      <th class="clickable" onclick="doSortScatterBy('category')">Kategorie</th>
      <th class="clickable" onclick="doSortScatterBy('description')">Notiz</th>
      <th style="min-width: 60px"></th>
    </tr>
  </thead>
  <tbody>

    <tr id="addRevenueInput">
      <td><input type="date" id="newItemDate" name="newItemDate" placeholder="Datum" onkeyup="isConfirmedNewItem(event)"></td>
      <td><input type="text" id="newItemName" name="newItemName" placeholder="Name" onkeyup="isConfirmedNewItem(event)"></td>
      <td><input type="text" id="newItemTitle" name="newItemTitle" placeholder="Beschreibung" onkeyup="isConfirmedNewItem(event)"></td>
      <td><input type="text" id="newItemAmount" name="newItemAmount" placeholder="Betrag (€)" onkeyup="isConfirmedNewItem(event)"></td>
      <td><input type="text" id="newItemCategory" name="newItemCategory" list="catlist" placeholder="Kategorie" onkeyup="isConfirmedNewItem(event)"></td>
      <td><input type="text" id="newItemDescription" name="newItemDescription" placeholder="Notiz" onkeyup="isConfirmedNewItem(event)"></td>
      <td><img src="/static/new.png" id="button-newItemInput" class="clickable dontshow" onclick="submitNewItem()"></td>
    </tr>

% therange = range(len(scatter['date']) - 1, -1, -1) if reverseSort else range(0, len(scatter['date']))
% for i in therange:
  % if theX is None or scatter['theX'][i] == theX:
    % date = scatter['date'][i]
    % name = scatter['name'][i]
    % shortname = scatter['name'][i][0:20]
    % title = scatter['title'][i]
    % account = scatter['account'][i]
    % theid = scatter['id'][i]
    % shorttitle = scatter['title'][i][0:40]
    % amountcurrency = str(scatter['amount'][i]) + scatter['currency'][i]
    % thecategory = '' if scatter['category'][i] == 'nicht kategorisiert' else scatter['category'][i]
    % description = scatter['description'][i]
    %
    % include('categoryItem.tpl', date=date, name=name, shortname=shortname, title=title, account=account, theid=theid, shorttitle=shorttitle, amountcurrency=amountcurrency, thecategory=thecategory, description=description)
  %end
%end
  </tbody>
</table>
</form>
</div>
