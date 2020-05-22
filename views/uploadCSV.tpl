<!DOCTYPE html>

<html>
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>konto</title>
  <link rel="stylesheet" type="text/css" href="/static/css/style.css">
</head>
<body>

% include('menu.tpl', site=site)

<form action="/uploadCSV" method="post" enctype="multipart/form-data">
 <fieldset>
  <legend>upload csv file</legend>
  <label for="uploadfile">csv file:</label>
  <input type="file" id="uploadfile" name="upload" /><br />

  <label for="account">account:</label>
  <input type="text" name="account" /><br />

  <label for="dateformat">date format:</label>
  <input type="text" name="dateformat" value="%d.%m.%Y" /><br />

  <label for="encoding">encoding:</label>
  <input type="text" id="encoding" name="encoding" value="iso-8859-15" /><br />

  <label for="locale">locale:</label>
  <input type="text" name="locale" id="locale" value="de_DE" /><br />

  <label for="delimiter">delimiter:</label>
  <input type="text" id="delimiter" name="delimiter" value=";" /><br />

  <label for="quotechar">quotechar:</label>
  <input type="text" id="quotechar" name="quotechar" value="&quot;" /><br />
 </fieldset>

 <fieldset>
  <legend>parser settings</legend>
  <label for="skiplines">ignore first n lines:</label>
  <input type="text" id="skiplines" name="skiplines" value="13" /><br />

  <label for="daterow">date row:</label>
  <input type="text" id="daterow" name="daterow" value="0" /><br />

  <label for="namerow">name row:</label>
  <input type="text" id="namerow" name="namerow" value="3" /><br />

  <label for="descriptionrow">description row:</label>
  <input type="text" id="descriptionrow" name="descriptionrow" value="8" /><br />

  <label for="amountrow">amount row:</label>
  <input type="text" id="amountrow" name="amountrow" value="11" /><br />

  <label for="sollhabenrow">(debit/credit row:)</label>
  <input type="text" id="sollhabenrow" name="sollhabenrow" value="12" /><br />

  <label for="currencyrow">(currency row:)</label>
  <input type="text" id="currencyrow" name="currencyrow" value="10" />
 </fieldset>
 <input type="submit" value="next ..." />
</form>

<p style="color: lightgray;margin-top: 3em;margin-left:1em">konto &mdash; &copy;<a href="https://github.com/mtill/konto" target="_blank" style="text-decoration:none;color: lightgray">Michael Till Beck</a>, 2018-2020</p>
</body>
</html>

