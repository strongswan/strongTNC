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
	maxlength: 50,
	remote: {
	  url: "/groups/check",
	  type: "post",
	  data: {
	    group: function() {
	      return $('#groupId').val()
	    },
	    name: function() {
	      return $("#name").val()
	    },
	    csrfmiddlewaretoken: csrftoken,
	  }
	}
      }
    },
    messages: {
      name: {
	remote: "Already exists!"
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
	maxlength: 50,
	remote: {
	  url: "/policies/check/" + $("#policyId").val(),
	  type: "post",
	  data: {
	    name: function() {
	      return $("#name").val()
	    },
	    csrfmiddlewaretoken: csrftoken,
	  }
	}
      },
      type: {
	required: true,
	regex: /^[0-9]+$/
      },
      range: {
	required: true,
	regex: /^ *\d+ *(- *\d+ *)?( *,*( *\d+ *)( *- *\d+ *)?)*$/
      },
      fail: {
	required: true
      },
      noresult: {
	required: true
      }
    },
    messages: {
      name: {
	remote: "Already exists!"
      },
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
	required: true,
	remote: {
	  url: "/enforcements/check",
	  type: "post",
	  data: {
	    policy: function() {
	      return $("#policy").val()
	    },
	    group: function() {
	      return $("#group").val()
	    },
	    enforcement: function() {
	      return $("#enforcementId").val()
	    },
	    csrfmiddlewaretoken: csrftoken,
	  }
	}
      },
      group: {
	required: true,
	remote: {
	  url: "/enforcements/check",
	  type: "post",
	  data: {
	    policy: function() {
	      return $("#policy").val()
	    },
	    group: function() {
	      return $("#group").val()
	    },
	    enforcement: function() {
	      return $("#enforcementId").val()
	    },
	    csrfmiddlewaretoken: csrftoken,
	  }
	}
      },
      max_age: {
	required: true,
	range: [0, 9223372036854775] // sqlite max value 
      }
    },
    messages: {
      group: {
	remote: "Enforcement already exists!"
      },
      policy: {
	remote: "Enforcement already exists!"
      }
    },
    groups: {
	    policy_group: "policy group"
    },
    highlight: function(element) {
      $(element).closest('.control-group').removeClass('success').addClass('error');
    },
    success: function(element) {
      element.addClass('valid').closest('.control-group').removeClass('error').addClass("invisiblevalid");;
    },
    errorPlacement: function(error, element) {
	    if(element.attr("id") == "policy"){
		    error.insertAfter("#group");
	    } else {
		    error.insertAfter(element);
	    }
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
	maxlength: 50,
	remote: {
	  url: "/packages/check/" + $("#packageId").val(),
	  type: "post",
	  data: {
	    name: function() {
	      return $("#name").val()
	    },
	    csrfmiddlewaretoken: csrftoken,
	  }
	}
      }
    },
    messages: {
      name: {
	remote: "Already exists!"
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
	maxlength: 50,
	remote: {
	  url: "/products/check",
	  type: "post",
	  data: {
	    product: function() {
	      return $('#productId').val()
	    },
	    name: function() {
	      return $("#name").val()
	    },
	    csrfmiddlewaretoken: csrftoken,
	  }
	}
      }
    },
    messages: {
      name: {
	remote: "Already exists!"
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
    }, "Please check your input."
  );

}); // end document.ready
