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
      element.addClass('valid').closest('.control-group').removeClass('error').addClass('success');
    }
  });

  $('#deviceform').validate({
    rules: {
      value: {
	required: true,
	maxlength: 50,
	regex: "^[a-f0-9]+$"
      },
      description: {
	required: true
      },
      product: {
	required: true
      }
    },
    highlight: function(element) {
      $(element).closest('.control-group').removeClass('success').addClass('error');
    },
    success: function(element) {
      element.addClass('valid').closest('.control-group').removeClass('error').addClass("invisiblevalid");;
    }
  });
  
  $('#packageform').validate({
    rules: {
      name: {
	required: true,
	maxlength: 50
      }
    },
    highlight: function(element) {
      $(element).closest('.control-group').removeClass('success').addClass('error');
    },
    success: function(element) {
      element.addClass('valid').closest('.control-group').removeClass('error').addClass("invisiblevalid");;
    }
  });
  
  $('#productform').validate({
    rules: {
      name: {
	required: true,
	maxlength: 50
      }
    },
    highlight: function(element) {
      $(element).closest('.control-group').removeClass('success').addClass('error');
    },
    success: function(element) {
      element.addClass('valid').closest('.control-group').removeClass('error').addClass("invisiblevalid");;
    }
  });
  
  $.validator.addMethod("regex",
        function(value, element, regexp) {
            var re = new RegExp(regexp);
            return this.optional(element) || re.test(value);
        },
        "Please check your input."
  );
  
}); // end document.ready