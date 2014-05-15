%ArticleTitle, Abstract, JournalTitle, queryPhrase, dayStr, authorStr, affiliation, DoiIdLinkStr, PMIDLinkStr, pinLinkStr, pinStr, listLinkStr = args

<!DOCTYPE html>
<html lang="en">
	<head>
	    <meta charset="utf-8">
	    <meta http-equiv="X-UA-Compatible" content="IE=edge">
	    <meta name="viewport" content="width=device-width, initial-scale=1.0">
	    <meta name="description" content="">
	    <meta name="author" content="Paul Laros">
	    <link rel="shortcut icon" href="favicon.ico">
	
	    <title> Scooply [alpha] -- {{ArticleTitle}} </title>
	    
	    <!-- Fonts -->
	    <link href="http://fonts.googleapis.com/css?family=Source+Sans+Pro%3A400%2C400italic%2C700" rel="stylesheet">
	    <link href="http://fonts.googleapis.com/css?family=Varela+Round" rel="stylesheet">
	    <!-- Bootstrap core CSS -->
	    <link href="css/bootstrap.min.css" rel="stylesheet">
	    <link href="css/font-awesome.min.css" rel="stylesheet">
	    <link href="css/bootstrap-social.css" rel="stylesheet">
	    <!-- Styles -->
	    <link href="css/main.css" rel="stylesheet">
	    <!-- Loading bar -->
	    <script src="js/pace.min.js"></script>
	    <!-- HTML5 shiv for IE8 support -->
	    <!--[if lt IE 9]>
	    	<script src="https://oss.maxcdn.com/libs/html5shiv/3.7.0/html5shiv.js"></script>
	    <![endif]-->
		<!-- JQuery-->
			<script src="js/jquery-1.11.0.min.js"></script>
		<script>
			$(document).ready(function(){
				$("#menu-container").hide();
				$("#toggle-menu").click(function(){
				$("#menu-container").slideToggle("50");
				$(".main-sections").slideToggle("50");
				});
			});
		</script>	
	</head>
	
	<body>
		<!-- Fixed navbar -->
	    <div class="navbar navbar-default navbar-fixed-top" role="navigation">
	     
	        <div class="navbar-header">
				<a rel="home" title="Scooply" href="/">
					<h1 class="site-title"> Scooply [alpha] </h1>
				</a>
				<div id="toggle-menu" class="btn btn-primary btnMenu">
					<i class="fa fa-align-justify"></i>
				</div>			
			</div>
			
			<div id="menu-container">
				<div class="col-xs-6 col-ld-6">
					<ul class="fa-ul">

						<a href="#"><li> Nature <span class="badge">43</span></li></a>
						<a href="#"><li> Science <span class="badge">3</span></li></a>
						<a href="#"><li> Cell <span class="badge">13</span></li></a>
						<a href="#"><li> telomerase <span class="badge">5</span></li></a>
					
					</ul>
				</div>
				<div class="col-xs-6 col-ld-6">
					<ul>
						<a href="#"><li> All <span class="badge">43</span></li></a>
						<a href="#"><li> Pinned <span class="badge">25</span></li></a>
						<a href="#"><li> Settings </li></a>
						<a href="#"><li> Feedback </li></a>
						<a href="/signout"><li></i> Sign out </li></a>

					</ul>
				</div>
			</div><!-- menu-container -->

	    </div>
	
	    <div id="primary" class="container">
	    	<div class="content">
	    	
		        	<section class="post">
							
							<header class="entry-header">
	
								<h2 class="entry-title">{{ArticleTitle}}</h2>
								<p class="entry-date"> 
									{{dayStr}} in <a class="label label-danger" href="#">{{JournalTitle}}</a>
									%if queryPhrase != JournalTitle:
										 on <a class="label label-primary" href="#">{{queryPhrase}}</a> 								
									%end
								</p>
																
								<p> 
									%if DoiIdLinkStr != '':
										 <a class="label label-primary" href="{{DoiIdLinkStr}}"> View in {{JournalTitle}} </a> &nbsp;
									%end
									%if PMIDLinkStr != '':
										 <a class="label label-primary" href="{{PMIDLinkStr}}"> View in PubMed </a> &nbsp;
									%end
										 <a class="label label-primary" href="{{pinLinkStr}}"> {{pinStr}} </a> &nbsp;
										 %#<a href="{{listLinkStr}}"> List </a>				
								</p>								
								
								%if authorStr.find('and'):
								%	authorPrefix = 'Authors'
								%else:
								%	authorPrefix = 'Author'
								%end
								<p> <b>{{authorPrefix}}:</b> {{authorStr}} </p>
				
								<p> <b>Affiliation:</b> {{affiliation}} </p>
				
								<p> <b>Abstract:</b> {{Abstract}} </p>
				
							  	<div class="entry-icon">
									<span class="glyphicon glyphicon-trash"></span> &nbsp;&nbsp;
									<span class="glyphicon glyphicon-bookmark"></span>
								</div>				
																
								%#<p> {{authorField}} </p>
								
							</header>
							
		        	</section> <!-- /.post -->
			        				        				        					
		        <footer class="footer">
		          <p>© Scooply 2014. Web design powered by Von. </p>
				</footer> <!-- /footer -->
	
	      	</div> <!-- class="content" -->
	    </div> <!-- /#primary -->

	</body>

</html>