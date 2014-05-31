var ajaxSpinner = {
    element: $("#hero"),
    enable: function () {
        this.element.spin();
    },
    disable: function () {
        this.element.spin(false);
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
    errorCallback: function() {},
    ajaxFunction: null,

    queryUpdate: function (newQuery) {
        this.query = newQuery;
        if (this.lastDelayedCall != null) {
            this.cancelLastDelayedCall();
        }
        this.startDelayedCall();
    },

    startDelayedCall: function () {
        this.lastDelayedCall = window.setTimeout(this.autocompleteCall, this.delay);
    },

    cancelLastDelayedCall: function () {
        window.clearTimeout(this.lastDelayedCall);
    },

    autocompleteCall: function () {
        // function is called by setTimeout,
        // thus it's running in the context of the window object
        var data = {'search_term': autocompleteDelay.query};
        var config = {'error_callback': autocompleteDelay.errorCallback};
        autocompleteDelay.ajaxFunction(autocompleteDelay.callback, data, config);
    }
};
