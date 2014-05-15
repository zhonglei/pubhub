$(showSidebar(){

	var toggleSidebar = $("#togglesidebar");
	var primary = $("#primary");
	var secondary = $("#secondary");

	if(secondary.style.display=="none"){
		secondary.css('display', 'none');
	} 
	else {
		secondary.css('display', 'inline-block');
	}
			
	});

});