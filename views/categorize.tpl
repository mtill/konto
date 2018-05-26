<h2>{{title}}</h2>

% import json

<datalist id="catlist">
</datalist>

<script class="code" type="text/javascript">
  allcategoriesNames = {{! json.dumps(allcategoriesNames)}};
</script>

<table>
  <tr><th>Datum</th><th>Name</th><th>Beschreibung</th><th>Betrag</th><th>Kategorie</th></tr>

% for i in range(len(scatter['date']) - 1, -1, -1):
  % if theX is None or scatter['theX'][i] == theX:
    % date = scatter['date'][i]
    % name = scatter['name'][i]
    % shortname = scatter['name'][i][0:15]
    % title = scatter['title'][i]
    % theid = scatter['id'][i]
    % shorttitle = scatter['title'][i][0:30]
    % amountcurrency = str(scatter['amount'][i]) + scatter['currency'][i]
    % thecategory = '' if scatter['category'][i] == 'nicht kategorisiert' else scatter['category'][i]
    <tr id="entry-{{theid}}">
      <td>{{date}}</td>
      <td title="{{name}}">{{shortname}}</td>
      <td title="{{title}}">{{shorttitle}}</td>
      <td>{{amountcurrency}}</td>
      <td>
        <input type="text" id="item-{{theid}}" origValue="{{thecategory}}" list="catlist" value="{{thecategory}}" oninput="activateButton('{{theid}}')">
        <img src="/static/ok.png" id="button-{{theid}}" style="display:none" onclick="categorize('{{theid}}')">
      </td>
    </tr>
  %end
%end

</table>
