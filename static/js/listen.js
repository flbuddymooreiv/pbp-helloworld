(function(globals) {
    'use strict';

    globals.listen = {};

    globals.listen.start = function(callback) {
        var longpoll = null;
        var unloadhandler = function(e) {
            longpoll && longpoll.abort();
        };
        $(window).on('beforeunload', unloadhandler);

        var latestknown = {
            val: 0
        };
        var config = function() {
            return {
                laterthan: latestknown.val,
                types: [{ type: 'testtype' }]
            };
        };

        longpoll = longpollmux.it(function(rsptime, rsp) {
            if (parseFloat(rsp) > latestknown.val) {
                latestknown.val = parseFloat(rsp);
            }
            callback && callback(rsp);
        }, config);
    };

})(this);
