%ArticleTitle, Abstract, JournalTitle, queryPhrase, dayStr, authorStr, affiliation, DoiIdLinkStr, PMIDLinkStr, pinLinkStr, pinStr, listLinkStr = args

<!DOCTYPE html>
<html lang="en">
    <head>
        <meta http-equiv="content-type" content="text/html; charset=UTF-8"> 
        <title>Scooply -- {{ArticleTitle}}</title>
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
		<div class="content_main">	
		
			<div class="article_info">
			
				<h3> <b> {{ArticleTitle}} </b> </h3>

				<h4> 
					{{dayStr}} in <span class="label label-default">{{JournalTitle}}</span>
				</h4>

		%if queryPhrase != JournalTitle:
				<h4> 
					Alert on <span class="label label-default">{{queryPhrase}}</span> 
				</h4>
		%end

				<p class="alignleft"> 
					|
		%if DoiIdLinkStr != '':
					 <a href="{{DoiIdLinkStr}}"> {{JournalTitle}} </a> |
		%end
		%if PMIDLinkStr != '':
					 <a href="{{PMIDLinkStr}}"> PubMed </a> |
		%end
					 <a href="{{pinLinkStr}}"> {{pinStr}} </a> |
					 %#<a href="{{listLinkStr}}"> List </a> |					
				</p>
			</div>
			<div style="clear: both;"></div>
			
			<div class="article_info">
						
				<p> <b>Abstract:</b> {{Abstract}} </p>

		%if authorStr.find('and'):
		%	authorPrefix = 'Authors'
		%else:
		%	authorPrefix = 'Author'
		%end
				<p> <b>{{authorPrefix}}:</b> {{authorStr}} </p>

				<p> <b>Affiliation:</b> {{affiliation}} </p>
				
			</div>			
			<div style="clear: both;"></div>

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