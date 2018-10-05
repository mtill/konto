<h2>{{title}} <img src="/static/download.png" class="clickable" onclick="doDownload(detailsParams)" alt="Umsätze exportieren"></h2>

% import json
% import datetime

<datalist id="catlist">
</datalist>

<script class="code" type="text/javascript">
  allcategoriesNames = {{! json.dumps(allcategoriesNames)}};
</script>

<div style="overflow-x:auto">
<table class="balance">
  <thead>
    <tr>
      <th class="clickable" onclick="doSortScatterBy('timestamp')">Datum</th>
      <th class="clickable" onclick="doSortScatterBy('name')">Name</th>
      <th class="clickable" onclick="doSortScatterBy('description')">Beschreibung</th>
      <th class="clickable" onclick="doSortScatterBy('amount')">Betrag</th>
      <th class="clickable" onclick="doSortScatterBy('category')">Kategorie</th>
      <th class="clickable" onclick="doSortScatterBy('note')">Notiz</th>
      <th style="min-width: 60px"></th>
    </tr>
  </thead>
  <tbody>

    <tr id="addRevenueInput">
      <td><input type="date" id="newItemDate" name="newItemDate" placeholder="Datum" onkeyup="isConfirmedNewItem(event)"></td>
      <td><input type="text" id="newItemName" name="newItemName" placeholder="Name" onkeyup="isConfirmedNewItem(event)"></td>
      <td><input type="text" id="newItemDescription" name="newItemDescription" placeholder="Beschreibung" onkeyup="isConfirmedNewItem(event)"></td>
      <td><input type="text" id="newItemAmount" name="newItemAmount" placeholder="Betrag (€)" onkeyup="isConfirmedNewItem(event)"></td>
      <td><input type="text" id="newItemCategory" name="newItemCategory" list="catlist" placeholder="Kategorie" onkeyup="isConfirmedNewItem(event)"></td>
      <td><input type="text" id="newItemNote" name="newItemNote" placeholder="Notiz" onkeyup="isConfirmedNewItem(event)"></td>
      <td><img src="/static/new.png" id="button-newItemInput" class="clickable dontshow" onclick="submitNewItem()"></td>
    </tr>

% therange = range(len(scatter['timestamp']) - 1, -1, -1) if reverseSort else range(0, len(scatter['timestamp']))
% for i in therange:
  % if theX is None or scatter['theX'][i] == theX:
    % timestamp = scatter['timestamp'][i]
    % name = scatter['name'][i]
    % shortname = scatter['name'][i][0:20]
    % description = scatter['description'][i]
    % shortdescription = scatter['description'][i][0:40]
    % account = scatter['account'][i]
    % theid = scatter['id'][i]
    % amountcurrency = '{:.2f}'.format(scatter['amount'][i]) + scatter['currency'][i]
    % thecategory = '' if scatter['category'][i] == 'nicht kategorisiert' else scatter['category'][i]
    % thenote = scatter['note'][i]
    %
    % date = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
    %
    % include('categoryItem.tpl', date=date, name=name, shortname=shortname, description=description, account=account, theid=theid, shortdescription=shortdescription, amountcurrency=amountcurrency, thecategory=thecategory, thenote=thenote)
  %end
%end
  </tbody>
</table>
</form>
</div>
