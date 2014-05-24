//******************************************
// Helper to set and get pseudo url-queries.
//******************************************
var HashQuery = {} || HashQuery;

// returns the query string after the url-hash
// as javascript object (key/value)
HashQuery.getHashQueryObject = function() {
    var hash = window.location.hash.slice(1);
    var result = {};
    if(hash) {
        var data = hash.split("&");
        for (var i = 0; i < data.length; i++) {
            var item = data[i].split("=");
            result[decodeURIComponent(item[0])] = decodeURIComponent(item[1]);
        }
    }
    return result;
};

// sets a key/value javascript object as pseudo
// query string after the url-hash
HashQuery.setHashQueryObject = function(obj) {
    var hash = '#';
    for(var key in obj) {
        hash +=
            encodeURIComponent(key) +
            "=" +
            encodeURIComponent(obj[key]) +
            "&";
    }
    window.location.hash = hash.slice(0,-1);
};

