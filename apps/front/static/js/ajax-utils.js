var ajaxSpinner = {
    element: $("#hero"),
    enable: function () {
        this.element.spin();
    },
    disable: function () {
        this.element.spin(false);
    }
};