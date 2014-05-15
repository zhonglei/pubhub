<!DOCTYPE html>
<html lang="en">
	<head>
	    <meta charset="utf-8">
	    <meta http-equiv="X-UA-Compatible" content="IE=edge">
	    <meta name="viewport" content="width=device-width, initial-scale=1.0">
	    <meta name="description" content="">
	    <meta name="author" content="Paul Laros">
	    <link rel="shortcut icon" href="favicon.ico">
	
	    <title> Scooply [alpha] </title>
	    
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

						%for q in listQueryPhrase: 
							%lenq = len([row for row in rows if row[0] == q])
							<a href="#{{q}}"><li> {{q}} <span class="badge">{{lenq}}</span></li></a>
						%end
					
					</ul>
				</div>
				<div class="col-xs-6 col-ld-6">
					<ul>
						<a href="#"><li> All <span class="badge">43</span></li></a>
						<a href="#"><li> Pinned <span class="badge">25</span></li></a>
						<a href="#"><li class="active-menu-item"> Settings </li></a>
						<a href="#"><li> Feedback </li></a>
						<a href="/signout"><li></i> Sign out </li></a>

					</ul>
				</div>
			</div><!-- menu-container -->

	    </div>
	
	    <div id="primary" class="container">
	    	<div class="content">
	    	
	    		%for q in listQueryPhrase:
					%rows2 = [row for row in rows if row[0] == q]
	    		
					<!-- Section title, could be either a journal or an alert-->
					<div class="section-title">
						<h1><a name="{{q}}"></a>{{q}}</h1>
					</div>

		        	<section class="post">

						%for row in rows2:
							%queryPhrase, ArticleTitle, JournalTitle, dayStr, authorField, affiliation, articleLinkStr = row
							
							<header class="entry-header">
	
								<h2 class="entry-title"><a href="{{articleLinkStr}}">{{ArticleTitle}}</a></h2>
								<p> {{authorField}} </p>
								<p class="entry-date"> 
									{{dayStr}} in <a class="label label-danger" href="#">{{JournalTitle}}</a>
									%if queryPhrase != JournalTitle:
										 on <a class="label label-primary" href="#">{{queryPhrase}}</a> 								
									%end
								</p>
							</header>
							
							<hr> 
							
				        %end #for row in rows2

		        	</section> <!-- /.post -->
			        				        				        	
			    %end #for q in listQueryPhrase
	
							
		        <footer class="footer">
		          <p>© Scooply 2014. Web design powered by Von. </p>
				</footer> <!-- /footer -->
	
	      	</div> <!-- class="content" -->
	    </div> <!-- /#primary -->

	</body>

</html>