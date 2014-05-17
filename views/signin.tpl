
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="">
    <meta name="author" content="">

    <title>Signin Template for Bootstrap</title>

    <!-- Bootstrap core CSS -->
    <link href="css/bootstrap.min.css" rel="stylesheet">

    <!-- Custom styles for this template -->
    <link href="css/sitetitle.css" rel="stylesheet">

    <!-- Just for debugging purposes. Don't actually copy this line! -->
    <!--[if lt IE 9]><script src="../../assets/js/ie8-responsive-file-warning.js"></script><![endif]-->

    <!-- HTML5 shim and Respond.js IE8 support of HTML5 elements and media queries -->
    <!--[if lt IE 9]>
      <script src="https://oss.maxcdn.com/libs/html5shiv/3.7.0/html5shiv.js"></script>
      <script src="https://oss.maxcdn.com/libs/respond.js/1.4.2/respond.min.js"></script>
    <![endif]-->
  </head>

  <body>

    <div class="container-fluid main-content">

		<div class="jumbotron">
				<h2>Scooply <br>\skoop-li\ :<br>timely, relevant and potentially game-changing</h2>
				<p>Scooply is the simplest way to keep you in touch with the latest research papers.</p>
		</div>
		
		<div class="col-xs-12 col-md-12 maintext-left">
        
	        <form class="navbar-form navbar-left" action="/signin" method="post">
	            <h3 class="form-signin-heading">Please sign in</h4>
	            <div class="form-group">
	            	<h4 class="form-signin-heading"><input name="email" type="text" autocapitalize="off" autocorrect="off" class="form-control" placeholder="suid" required>@stanford.edu</h4>
	            	<h4 class="form-signin-heading"> <input name="password" type="password" class="form-control" placeholder="Password" required>  </h4>
				</div>
	            <h4 class="form-signin-heading"><button class="btn btn-lg btn-primary btn-block" type="submit" >Sign in</button></h4>
	            <h4 class="form-signin-heading">New to scooply? <a href="/signup">Sign up</a></h4>
	        </form>
	        
		</div>

    </div> <!-- /container -->


    <!-- Bootstrap core JavaScript
    ================================================== -->
    <!-- Placed at the end of the document so the pages load faster -->
  </body>
</html>