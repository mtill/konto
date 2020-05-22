<ul>

% if site == 'month':
  <li><a class="active" href="/byCategory/month">monthly overview</a></li>
% else:
  <li><a href="/byCategory/month">monthly overview</a></li>
% end

% if site == 'year':
  <li><a class="active" href="/byCategory/year">yearly overview</a></li>
% else:
  <li><a href="/byCategory/year">yearly overview</a></li>
% end

% if site == 'sum':
  <li><a class="active" href="/sum">accumulated</a></li>
% else:
  <li><a href="/sum">accumulated</a></li>
% end

% if site == 'check':
  <li><a class="active" href="/check/current/3/showHeader">rules</a></li>
% else:
  <li><a href="/check/current/3/showHeader">rules</a></li>
% end

% if site == 'editCategories':
  <li><a class="active" href="/editCategories">categorize</a></li>
% else:
  <li><a href="/editCategories">categorize</a></li>
% end

% if site == 'uploadCSV':
  <li><a class="active" href="/uploadCSV">import CSV</a></li>
% else:
  <li><a href="/uploadCSV">import CSV</a></li>
% end

</ul>
