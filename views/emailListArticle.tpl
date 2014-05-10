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
	
	<h2>
		Scooply /skoop-li/
	</h2>
	<p> Hello {{name}}, </p>
	<p> This week's top-notch bioscience papers are ready to view! Check them out below.
	</p>
	<p>Your Scooply team</p>

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
		%queryPhrase, ArticleTitle, JournalTitle, dayStr, authorField, affiliation, recordAndRedirectStr = row
	
				<div class="article_info">
					<h4> 
						<a href="{{recordAndRedirectStr}}">{{ArticleTitle}}</a> <br>
						{{authorField}} <br>
						{{dayStr}} in <span class="label label-default">{{JournalTitle}}</span> <br>
			%if queryPhrase != JournalTitle:
						Alert on <span class="label label-default">{{queryPhrase}}</span>
			%end
					</h4>
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