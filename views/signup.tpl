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


        <h1>You are invited to Scooply's alpha test!</h1>

		<div class="content_main">
        
	        <form action="/signup" method="post" onsubmit="return validate(this);">
	        
	            <h3>Sign up with your Stanford email address</h3>
	            
	            <p>
	                Email: <input name="email" type="text" required />@stanford.edu <br>
	                
	                Password: <input name="password" type="password" required/>  <br>
	                Confirm password: <input name="passwordAgain" type="password" required />

	            </p>
	
	            <h3>Tell us a bit more about yourself</h3>
	
	            <p>
	                <b>What's your name?</b><br>
	                First: <input name="firstName" type="text" /> Last: <input name="lastName" type="text" />
	            </p>
	            
	            <p>
	                <b>What's your primary research area?</b><br>
	                <select name="areaId">
	                    <option value="1">Bioinformatics and computational genomics</option>
	                    <option value="2">Biophysics and bioengineering</option>
	                    <option value="3">Developmental biology, stem cell biology and genetics</option>
	                    <option value="4">Microbiology and immunology</option>
	                    <option value="5">Biochemistry, cell biology and molecular biology</option>
	                    <option value="6">Neurosciences</option>
	                    <option value="7">Clinical sciences</option>
	                </select> 
	            </p>
	            
	            <p>
	                <b>What specific research topics would you like to receive Scooply alerts on?</b> <br>
	                <textarea name="keywords" rows="8" cols="50" required placeholder="For example: telomeres and telomerase, noncoding RNA, mechanisms of aging. Please type each topic in a separate line."></textarea>
	            </p>
	            
	            <h3></h3>
	            
	            <p>
	            	<!-- 
	            	By clicking on Sign up, you agree to Scooply's terms & conditions and privacy policy <br> 
	            	-->
	
	                <input value="Sign up" type="submit" /> <br>
	                Already have an account? <a href="/signin">Sign in</a>
	            </p>
	            
	        </form>
        
		</div>
        
	<!-- jQuery (necessary for Bootstrap's JavaScript plugins) -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js"></script>
    <!-- Include all compiled plugins (below), or include individual files as needed -->
    <script src="js/bootstrap.min.js"></script>

     <!-- JavaScript jQuery code from Bootply.com editor -->
	<script type='text/javascript'>
	$(document).ready(function() {
	});
	</script>
	
	<script type='text/javascript'>
	function validate(form) {
		var e = form.elements;		
		/* validate passwords */
		if(e['password'].value != e['passwordAgain'].value) {
    		return false;
  		}
  		return true;
	}
	</script>
	
	<!-- Jasney-->
	<script src="jasny-bootstrap/js/jasny-bootstrap.min.js"></script>

    </body>

</html>        
