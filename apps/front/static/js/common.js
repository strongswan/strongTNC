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
    ajaxFunction: null,

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
        // function is called by setTimeout,
        // thus it's running in the context of the window object
        var data = {'search_term': autocompleteDelay.query};
        var config = {'error_callback': autocompleteDelay.errorCallback};
        autocompleteDelay.ajaxFunction(autocompleteDelay.callback, data, config);
    }
};

// Wrapper object to inject pre and post execute to Dajaxice requests.
// Used to show ajax loading status

DajaxWrapper = function($container) {
    this.$container = $container;
    this.ajaxLoader = null;
    this.preLoad = function() {
        this.$container.css({'min-height': '55px'});
        this.ajaxLoader = new ajaxLoader(this.$container);
        GlobalAjaxIndicator.showLoading();
    };

    this.postLoad = function() {
        this.ajaxLoader.remove();
        GlobalAjaxIndicator.hideLoading();
    };

    this.call = function(dajaxCall, callback, params, errorHandlers) {
        this.preLoad();
        errorHandlers = errorHandlers || {'error_callback': function(){}};
        var originalHandler = errorHandlers['error_callback'];

        var errorHandlerProxy = function handlerProxy() {
            originalHandler();
            this.postLoad();
        }.bind(this);

        errorHandlers['error_callback'] = errorHandlerProxy;

        var callbackProxy = function(data) {
            callback(data);
            this.postLoad();
        }.bind(this);

        dajaxCall(callbackProxy, params, errorHandlers);
    };
};

var GlobalAjaxIndicator = {
    loader: $("#global-loader"),
    showLoading: function() {
        if(!this._count) this.loader.show();
        ++this._count;
    },
    _count: 0,
    hideLoading: function() {
        --this._count;
        if(!this._count) this.loader.hide();
    }
};

