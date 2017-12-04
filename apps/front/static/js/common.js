/**
 * Common JavaScript functions that can be used on every page.
 *
 * Note that this script is loaded in the footer, so always wait for the
 * document ready event before accessing the DOM.
 */

/**
 * Link tags with the "history_back" function trigger "window.history.back()".
 */
$('body').on('click', 'a.history_back', function(event) {
    event.preventDefault();
    history.back();
});

// Default options for form validation
var validationDefaults = {
    errorClass: 'help-block',
    highlight: function (element) {
        $(element).closest('.form-group').addClass('has-error');
    },
    unhighlight:  function(element) {
        $(element).closest('.form-group').removeClass('has-error');
    }
};

// delay the request, to reduce the amount of requests
// --> the request is only sent if the query does not
//     change during a defined delay.
var autocompleteDelay = {
    delay: 600,
    query: '',
    lastDelayedCall: null,
    callback: null,
    errorCallback: function() {
    },
    ajaxUrl: null,

    queryUpdate: function(newQuery) {
        this.query = newQuery;
        if(this.lastDelayedCall != null) {
            this.cancelLastDelayedCall();
        }
        this.startDelayedCall();
    },

    startDelayedCall: function() {
        this.lastDelayedCall = window.setTimeout(this.autocompleteCall, this.delay);
    },

    cancelLastDelayedCall: function() {
        window.clearTimeout(this.lastDelayedCall);
    },

    autocompleteCall: function() {
        var config = {
            method: 'POST',
            url: autocompleteDelay.ajaxUrl,
            data: {'search_term': autocompleteDelay.query},
            success: autocompleteDelay.callback,
            error: autocompleteDelay.errorCallback,
        };
        $.ajax(config);
    }
};

function getCookie(name) {
    var value = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                value = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return value;
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$(document).ajaxStart(function() {
    $("#global-loader").show();
});
$(document).ajaxSend(function(event, xhr, settings) {
    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
    }
});
$(document).ajaxStop(function(xhr, status) {
    $("#global-loader").hide();
});
