$(document).ready(function(){

  // Validate
  // http://bassistance.de/jquery-plugins/jquery-plugin-validation/
  // http://docs.jquery.com/Plugins/Validation/
  // http://docs.jquery.com/Plugins/Validation/validate#toptions

  $('#signform').validate({
    rules: {
      username: {
	minlength: 2,
	required: true
      },
      password: {
	minlength: 2,
	required: true
      }
    },
    highlight: function(element) {
	    $(element).closest('.control-group').removeClass('success').addClass('error');
    },
    success: function(element) {
	    element
	    .addClass('valid')
	    .closest('.control-group').removeClass('error').addClass('success');
    }
  });

  $('#groupform').validate({
    debug: true,
    rules: {
      name: {
	maxlength: 50,
	required: true
      }
    },
    highlight: function(element) {
	    $(element).closest('.control-group').removeClass('success').addClass('error');
    },
    success: function(element) {
	    element
	    .addClass('valid')
	    .closest('.control-group').removeClass('error').addClass('success');
    }
  });
  
}); // end document.ready