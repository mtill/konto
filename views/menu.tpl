<ul>

% if site == 'month':
  <li><a class="active" href="/byCategory/month">Monatsübersicht</a></li>
% else:
  <li><a href="/byCategory/month">Monatsübersicht</a></li>
% end

% if site == 'year':
  <li><a class="active" href="/byCategory/year">Jahresübersicht</a></li>
% else:
  <li><a href="/byCategory/year">Jahresübersicht</a></li>
% end

% if site == 'profit':
  <li><a class="active" href="/profit">Gewinn</a></li>
% else:
  <li><a href="/profit">Gewinn</a></li>
% end

% if site == 'editCategories':
  <li><a class="active" href="/editCategories">Kategorisierung</a></li>
% else:
  <li><a href="/editCategories">Kategorisierung</a></li>
% end

</ul>
