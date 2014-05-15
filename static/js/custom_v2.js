function(){

	var toggleSidebar = $("#togglesidebar");
	var primary = $("#primary");
	var secondary = $("#secondary");

	toggleSidebar.on("click", function(){

		if(secondary.hasClass("displayOFF")){
			secondary.removeClass("displayOFF");
			secondary.addClass("displayON");

		}
		else {
			secondary.removeClass("displayOFF");
			secondary.addClass("displayON");
		}
	});

}