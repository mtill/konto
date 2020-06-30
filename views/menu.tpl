<ul>

% if site == 'month':
  <li><a class="active" href="/">debits and credits</a></li>
% else:
  <li><a href="/">debits and credits</a></li>
% end

% if site == 'check':
  <li><a class="active" href="/check/current/3/showHeader">validate rules</a></li>
% else:
  <li><a href="/check/current/3/showHeader">validate rules</a></li>
% end

% if site == 'editCategories':
  <li><a class="active" href="/editCategories">edit categories &amp; validation rules</a></li>
% else:
  <li><a href="/editCategories">edit categories &amp; validation rules</a></li>
% end

% if site == 'uploadCSV':
  <li><a class="active" href="/uploadCSV">import</a></li>
% else:
  <li><a href="/uploadCSV">import</a></li>
% end

</ul>
