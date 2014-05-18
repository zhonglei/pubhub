
<div class="col-xs-12 col-md-12 maintext-left">

    <form class="navbar-form navbar-left" action="/signup" method="post">
	
        <div class="form-group">
	        <h3 class="form-signin-heading">Sign up with your SUID</h3>
    
        	<h4 class="form-signin-heading"><input name="email" type="text" autocapitalize="off" autocorrect="off" class="form-control" placeholder="suid" required>@stanford.edu</h4>
        	<h4 class="form-signin-heading"> <input name="password" type="password" class="form-control" placeholder="Password" required>  </h4>
        	<h4 class="form-signin-heading"> <input name="passwordAgain" type="password" class="form-control" placeholder="Retype password" required>  </h4>
	
			<hr>
	
	        <h3 class="form-signin-heading">Tell us about yourself</h3>

	        <h4 class="form-signin-heading">
		        I work as a
	            <div class="btn-group">
	            	<button data-toggle="dropdown" class="btn btn-default dropdown-toggle">Ph.D. student <span class="caret"></span></button>
	              	<ul class="dropdown-menu">
	                	<li>
	                  		<input type="radio" name="phd" id="phd1" value="1" checked>
	                  		<label for="phd1">Ph.D.</label>
	                	</li>
	                	<li>
	                  		<input type="radio" name="phd" id="phd2" value="2">
	                  		<label for="phd2">Postdoc</label>
	                	</li>
	              	</ul>
	            </div>
			</h4>

	        <h4 class="form-signin-heading">
		        <p>My primary research interest is in </p>
	            <div class="btn-group">
	            	<button data-toggle="dropdown" class="btn btn-default dropdown-toggle">Bioinformatics and comput. genomics<span class="caret"></span></button>
	              	<ul class="dropdown-menu">
	                	<li>
	                  		<input type="radio" name="areaId" id="area1" value="1" checked>
	                  		<label for="area1">Bioinformatics and comput. genomics</label>
	                	</li>
	                	<li>
	                  		<input type="radio" name="areaId" id="area2" value="2">
	                  		<label for="area2">Biophysics and bioengineering</label>
	                	</li>
	                	<li>
	                  		<input type="radio" name="areaId" id="area3" value="3">
	                  		<label for="area3">Dev. / stem cell biology and genetics</label>
	                	</li>
	                	<li>
	                  		<input type="radio" name="areaId" id="area4" value="4">
	                  		<label for="area4">Microbiology and immunology</label>
	                	</li>
	                	<li>
	                  		<input type="radio" name="areaId" id="area5" value="5">
	                  		<label for="area5">Biochemistry, cell / molecular biology</label>
	                	</li>
	                	<li>
	                  		<input type="radio" name="areaId" id="area6" value="6">
	                  		<label for="area6">Neurosciences</label>
	                	</li>
	                	<li>
	                  		<input type="radio" name="areaId" id="area7" value="7">
	                  		<label for="area7">Clinical sciences</label>
	                	</li>
	              	</ul>
	            </div>
			</h4>
			
			<hr>
			
	        <h3 class="form-signin-heading">Set up your alerts</h3>
	        
	        <h4 class="form-signin-heading">
		        <p>I'd like to get Scooply alerts on </p>
	            <textarea class="form-control" name="keywords" rows="8" required placeholder="For example: telomeres and telomerase, noncoding RNA, mechanisms of aging. Please type each topic in a separate line."></textarea>
			</h4>

			
			
	        
		</div>
		
        <h4 class="form-signin-heading"><button class="btn btn-lg btn-primary btn-block" type="submit" >Sign up</button></h4>
        <h4 class="form-signin-heading">Already signed up? <a href="/signin">Sign in</a></h4>
    
    </form>
    
</div>


%rebase sitetitle title='Scooply sign up'

<!--    

	        <h4 class="form-signin-heading">
		        I work as a
	
	            <div class="btn-group">
	              <button data-toggle="dropdown" class="btn btn-default dropdown-toggle">Ph.D. student <span class="caret"></span></button>
	              <ul class="dropdown-menu">
	                <li>
	                  <input type="radio" id="ex1_1" value="1" checked>
	                  <label for="ex1_1">Ph.D. student</label>
	                </li>
	                <li>
	                  <input type="radio" id="ex1_2" value="2">
	                  <label for="ex1_2">Postdoc research scientist</label>
	                </li>
	              </ul>
	            </div>

			</h4>


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
	
	onsubmit="return validate(this);"            

-->
