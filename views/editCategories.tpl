<!DOCTYPE html>

<html>
 <head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <title>konto - Kategorien bearbeiten</title>
  <link rel="stylesheet" type="text/css" href="/static/style.css">
  <script class="include" type="text/javascript" src="/static/jquery-3.3.1.min.js"></script>
  <script class="include" type="text/javascript" src="/static/categorize.js"></script>
  <script type="text/javascript">
    function onItemCategorized(theid) {
      $('#entry-' + theid).hide();
    }
  </script>
 </head>
 <body>

% include('menu.tpl', site='editCategories')

  <form action="/editCategories" method="POST">
   <p>
<textarea name="categories" rows="20" cols="80">{{categories}}</textarea>
  </p>
   <input type="submit" value="Speichern">
  </form>

% include('categorize.tpl', scatter=uncategorized, theX=None, title="Umsätze ohne Kategorie:")

  <p style="color: lightgray;margin-top: 3em;margin-left:1em">konto &mdash; &copy;<a href="http://www.michaeltillbeck.de" target="_blank" style="text-decoration:none;color: lightgray">Michael Till Beck</a>, 2018</p>
 </body>
</html>
