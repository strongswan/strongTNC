$(document).ready(function(){

  // Validate
  // http://bassistance.de/jquery-plugins/jquery-plugin-validation/
  // http://docs.jquery.com/Plugins/Validation/
  // http://docs.jquery.com/Plugins/Validation/validate#toptions

  $('#groupform').validate({
    debug: true,
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
      element.addClass('valid').closest('.control-group').removeClass('error').addClass('success');
    }
  });

  $('#policyform').validate({
    rules: {
      name: {
	required: true,
	maxlength: 50
      },
      type: {
	required: true,
	regex: /^[0-9]+$/
      },
      range: {
	required: true,
	regex: /^\s*\d+\s*(-*\s*\d+\s*)?( *,*(\s*\d+\s*)( *-*\s*\d+\s*)?)*$/
      },
      fail: {
	required: true
      },
      noresult: {
	required: true
      }
    },
    messages: {
      type: {
	regex: "This field is required."
      }
    },
    highlight: function(element) {
      $(element).closest('.control-group').removeClass('success').addClass('error');
    },
    success: function(element) {
      element.addClass('valid').closest('.control-group').removeClass('error').addClass("invisiblevalid");;
    }
  });  
  
  $('#enforcementform').validate({
    rules: {
      policy: {
	required: true
      },
      group: {
	required: true
      },
      max_age: {
	required: true,
	range: [0, 9223372036854775] // sqlite max value 
      }
    },
    highlight: function(element) {
      $(element).closest('.control-group').removeClass('success').addClass('error');
    },
    success: function(element) {
      element.addClass('valid').closest('.control-group').removeClass('error').addClass("invisiblevalid");;
    }
  });
  
  $('#deviceform').validate({
    rules: {
      value: {
	required: true,
	maxlength: 50,
	regex: /^[a-f0-9]+$/
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