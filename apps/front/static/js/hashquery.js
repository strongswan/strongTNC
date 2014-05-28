//******************************************
// Helper to set and get pseudo url-queries.
//******************************************
var HashQuery = {ignoreEvents: false, hash: {}, callbacks: {}} || HashQuery;

// returns the query string after the url-hash
// as javascript object (key/value)
HashQuery.getHashQueryObject = function () {
    var hash = window.location.hash.slice(1);
    var result = {};
    if (hash) {
        var data = hash.split("&");
        for (var i = 0; i < data.length; i++) {
            var item = data[i].split("=");
            result[decodeURIComponent(item[0])] = decodeURIComponent(item[1]);
        }
    }
    return result;
};

HashQuery.sendChanged = function (key, value) {
    var listeners = HashQuery.callbacks[key];
    for (var i = 0; i < listeners.length; ++i) {
        listeners[i](key, value);
    }
};

HashQuery.notifyAll = function () {
    if (HashQuery.ignoreEvents) {
        HashQuery.ignoreEvents = false;
        return;
    }

    var obj = HashQuery.getHashQueryObject();
    for (var key in obj) {
        var key_enc = encodeURIComponent(key);
        var val_enc = encodeURIComponent(obj[key]);

        if (HashQuery.callbacks[key_enc] && HashQuery.hash[key_enc] != val_enc) {
            $.each(HashQuery.callbacks[key_enc], function (idx, callback) {
                callback(key_enc, val_enc);
            });
        }
    }

    HashQuery.hash = HashQuery.getHashQueryObject();
};

HashQuery.addChangedListener = function (tag, callback) {
    if (HashQuery.callbacks[tag]) {
        HashQuery.callbacks[tag].push(callback);
    }
    else {
        HashQuery.callbacks[tag] = [callback];
    }
};

HashQuery.setHashKey = function (obj, ignoreEvents, avoidBrowserHistory) {
    var current_obj = HashQuery.getHashQueryObject();
    for (var key in obj) {
        current_obj[key] = obj[key];
    }
    HashQuery.setHashQueryObject(current_obj, ignoreEvents, avoidBrowserHistory);
};

// sets a key/value javascript object as pseudo
// query string after the url-hash
HashQuery.setHashQueryObject = function (obj, ignoreEvents, avoidBrowserHistory) {
    var hash = '#';
    for (var key in obj) {
        hash +=
            encodeURIComponent(key) +
            "=" +
            encodeURIComponent(obj[key]) +
            "&";

    }
    HashQuery.ignoreEvents = ignoreEvents;
    if(avoidBrowserHistory) {
        window.location.replace(hash.slice(0, -1));
    } else {
        window.location.hash = hash.slice(0, -1);
    }
};

window.addEventListener("hashchange", HashQuery.notifyAll, false);
HashQuery.hash = HashQuery.getHashQueryObject();