/**
 * strongTNC validation rules.
 *
 * Copyright (C) 2013 Marco Tanner
 * Copyright (C) 2013 Stefan Rohner
 * HSR University of Applied Sciences Rapperswil
 *
 * Licensed under the GNU Affero General Public License:
 *   http://www.gnu.org/licenses/agpl-3.0.html
 */
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
	  url: "/policies/check",
	  type: "post",
	  data: {
	    policy: function() {
	      return $('#policyId').val()
	    },
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
    },
    errorPlacement: function(error, element) {
      if (element.attr("id") == "type") {
	error.insertAfter("#type_chzn");
      } else if (element.attr("id") == "fail"){
        error.insertAfter("#fail_chzn");
      } else if (element.attr("id") == "noresult"){
	error.insertAfter("#noresult_chzn");
      } else {
	error.insertAfter(element)
      }
    },
    ignore: ":hidden:not(.chzn-select)",
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
    },
    errorPlacement: function(error, element) {
      if (element.attr("id") == "product") {
	error.insertAfter("#product_chzn");
      } else {
	error.insertAfter(element)
      }
    },
    ignore: ":hidden:not(.chzn-select)",
  });

  $('#packageform').validate({
    rules: {
      name: {
	required: true,
	maxlength: 50,
	remote: {
	  url: "/packages/check",
	  type: "post",
	  data: {
	    package: function() {
	      return $('#packageId').val()
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
