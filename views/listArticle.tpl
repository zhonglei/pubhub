<!DOCTYPE html>
<html lang="en">
    <head>
        <meta http-equiv="content-type" content="text/html; charset=UTF-8"> 
        <title>sCoopLy</title>
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
	<!-- Update in this div -->
	
				
			<nav id="myNavmenu" class="navmenu navmenu-default navmenu-fixed-left offcanvas" role="navigation">

				<a class="navmenu-brand" href="#">sCoopLy</a>
				  
				<ul class="nav navmenu-nav">
					<li class="active"><a href="#">Home</a></li>
					<li><a href="#">Nature</a></li>
					<li><a href="#">Science</a></li>
					<li><a href="#">Cell</a></li>
				</ul>
		
			</nav>
						
		<div class="content_main">
			
%for row in rows:
	%ArticleTitle, JournalTitle, dayStr, authorField, affiliation, recordAndRedirectStr = row
			<div class="article_info">
				<h3><a href="{{recordAndRedirectStr}}">{{ArticleTitle}}</a> </h3>
				<h4> {{authorField}} </h4>
				<h4> {{dayStr}} in <span class="label label-default">{{JournalTitle}}</span></h4>
			</div> 
	
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