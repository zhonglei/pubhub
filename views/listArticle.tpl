<!DOCTYPE html>
<html lang="en">
    <head>
        <meta http-equiv="content-type" content="text/html; charset=UTF-8"> 
        <title>Scooply</title>
        <meta name="generator" content="Bootply" />
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
        <!--Bootstrap-->
		<link href="css/bootstrap.min.css" rel="stylesheet">
		<!--Jasny-->
		  <link href="jasny-bootstrap/css/jasny-bootstrap.min.css" rel="stylesheet">
		<!--- Style sheet for this template-->
		<link href="css/scooply-v3.css" rel="stylesheet">
        <!--[if lt IE 9]>
          <script src="//html5shim.googlecode.com/svn/trunk/html5.js"></script>
        <![endif]-->
    </head>
    
	<body>
	
		<h1>
			Scooply /skoop-li/
		</h1>

%listQueryPhrase = [row[0] for row in rows] #first element is queryPhrase
%listQueryPhrase = list(set(listQueryPhrase)) # distinct
%#bring to print Nature, Science and Cell
%if 'Cell' in listQueryPhrase:
%	listQueryPhrase.insert(0, listQueryPhrase.pop(listQueryPhrase.index('Cell')))
%end
%if 'Science' in listQueryPhrase:
	%listQueryPhrase.insert(0, listQueryPhrase.pop(listQueryPhrase.index('Science')))
%end
%if 'Nature' in listQueryPhrase:
	%listQueryPhrase.insert(0, listQueryPhrase.pop(listQueryPhrase.index('Nature')))
%end

		<div class="outline">				
			<h4>
				<ul>
%for q in listQueryPhrase: 
	%lenq = len([row for row in rows if row[0] == q])
					<li><a href="#{{q}}">{{q}} ({{lenq}} new)</a></li>
%end
				</ul>
			</h4>		
		</div>
						
		<div class="content_main">
		
%for q in listQueryPhrase:

	%rows2 = [row for row in rows if row[0] == q]
	
			<h3>
				<a name="{{q}}">{{q}}</a>
			</h3>
					
	%for row in rows2:
		%queryPhrase, ArticleTitle, JournalTitle, dayStr, authorField, affiliation, articleLinkStr = row
	
				<div class="article_info">
					<h3> <a href="{{articleLinkStr}}" target="_blank">{{ArticleTitle}}</a> </h3>
					<h4> {{authorField}} </h4>
					<h4> 
						{{dayStr}} in <span class="label label-default">{{JournalTitle}}</span>
					</h4>
		%if queryPhrase != JournalTitle:
					<h4> 
						Alert on <span class="label label-default">{{queryPhrase}}</span> 
					</h4>
		%end
				</div>
	%end	

%end


			
		</div><!-- content_main-->

    
	<!-- jQuery (necessary for Bootstrap's JavaScript plugins) -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js"></script>
    <!-- Include all compiled plugins (below), or include individual files as needed -->
    <script src="js/bootstrap.min.js"></script>

     <!-- JavaScript jQuery code from Bootply.com editor -->
	<script type='text/javascript'>
	$(document).ready(function() {
	});
	</script>
	
	<!-- Jasney-->
	<script src="jasny-bootstrap/js/jasny-bootstrap.min.js"></script>

    </body>

</html>