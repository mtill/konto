<tr id="entry-{{theid}}">
  <td title="{{account}}">{{date}}</td>
  <td title="{{name}}">{{shortname}}</td>
  <td title="{{title}}">{{shorttitle}}</td>
  <td>{{amountcurrency}}</td>
  <td style="margin-left:0px">
    <input type="text" id="item-{{theid}}" list="catlist" placeholder="Kategorie" value="{{thecategory}}" onkeyup="isConfirmed(event, '{{theid}}')">
  </td>
  <td>
    <input type="text" id="description-{{theid}}" placeholder="Notiz" value="{{description}}" onkeyup="isConfirmed(event, '{{theid}}')">
  </td>
  <td>
    <img src="/static/ok.png" id="button-{{theid}}" class="clickable dontshow" onclick="updateItem('{{theid}}')">
    %if account == 'Bargeld':
    <img src="/static/delete.png" class="clickable" onclick="showDetails(detailsParams, 'deleteItem', '{{theid}}')">
    %end
  </td>
</tr>
