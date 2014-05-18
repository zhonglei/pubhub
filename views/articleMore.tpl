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
	
	    <title> Scooply -- {{ArticleTitle}} </title>
	    
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
	
		%include navbar
			
	    <div id="primary" class="container">
	    	<div class="content">
	    	
		        	<section class="post">
							
							<header class="entry-header">
	
								<h2 class="entry-title">{{ArticleTitle}}</h2>
								<p class="entry-date"> 
									{{dayStr}} in <span class="label label-danger">{{JournalTitle}}</span>
									%if queryPhrase != JournalTitle:
										 on <span class="label label-warning">{{queryPhrase}}</span> 								
									%end
								</p>

								<p> 
									%if DoiIdLinkStr != '':
										 <a class="label label-primary" href="{{DoiIdLinkStr}}">View in {{JournalTitle}}</a> &nbsp;
									%end
									%if PMIDLinkStr != '':
										 <a class="label label-primary" href="{{PMIDLinkStr}}">View in PubMed</a> &nbsp;
									%end
										 <a class="label label-primary" href="{{pinLinkStr}}">{{pinStr}}</a> &nbsp;
										 %#<a href="{{listLinkStr}}"> List </a>				
								</p>								
								
								%if authorStr.find('and'):
								%	authorPrefix = 'Authors'
								%else:
								%	authorPrefix = 'Author'
								%end
								<p> <strong>{{authorPrefix}}:</strong> {{authorStr}} </p>
				
								<p> <strong>Affiliation:</strong> {{affiliation}} </p>
				
								<p> <strong>Abstract:</strong> {{Abstract}} </p>
				
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