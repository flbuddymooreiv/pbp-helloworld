(function(globals) {

    globals.longpollmux = globals.longpollmux || {};
    u = globals.longpollmux;

    u.it = function(onbreak, config) {
        var ANALYZE_INTERVAL = 103;
        var MAX_AGE = 2500;
        var MAX_SUMMARY_AGE = 500;

        var PREFIX = 'longpollmux-';

        var SUMMARYKEY = PREFIX + 'summary';
        var SUMMARYLASTUPDATEKEY = PREFIX + 'summarylastupdate';
        var LASTCONFIGSKEY = PREFIX + 'lastconfigs';

        var STARTPREFIX = PREFIX + 'start-';
        var LASTUPDATEPREFIX = PREFIX + 'lastupdate-';
        var CONFIGPREFIX = PREFIX + 'config-';
        var RESPONSEPREFIX = PREFIX + 'response-';
        var RESPONSETIMEPREFIX = PREFIX + 'responsetime-';

        var prefixfunc = function(prefix) {
            return function(id) { return prefix + id };
        };

        var startkey = prefixfunc(STARTPREFIX);
        var updatekey = prefixfunc(LASTUPDATEPREFIX);
        var configkey = prefixfunc(CONFIGPREFIX);
        var responsekey = prefixfunc(RESPONSEPREFIX);
        var responsetimekey = prefixfunc(RESPONSETIMEPREFIX);

        var testfunc = function(prefix) {
            return function(k, undefok) {
                return new RegExp(prefix + '[0-9]+').test(k) ||
                    (undefok && k == prefix + 'undefined');
            }
        };

        var isstartkey = testfunc(STARTPREFIX);
        var isupdatekey = testfunc(LASTUPDATEPREFIX);
        var isconfigkey = testfunc(CONFIGPREFIX);
        var isresponsekey = testfunc(RESPONSEPREFIX);
        var isresponsetimekey = testfunc(RESPONSETIMEPREFIX);

        var timeInt = function(key) {
            return parseInt(localStorage[key]); };

        var longpollmux = function(onbreak, config) {
            var safestarttime = new Date().getTime();
            var starttime = new Date().getTime();
            var myid = Math.floor(Math.random() * 1000000);
            var longpoll = null;

            var agefunc = function(key) {
                var curtime = new Date().getTime();
                return key in localStorage ?
                    curtime - timeInt(key) : null;
            };

            var clearstate = function(removesoul) {
                longpoll && longpoll.abort();
                longpoll = null;
                delete localStorage[responsekey(myid)];
                delete localStorage[responsetimekey(myid)];
                if (removesoul) {
                    removesoul && delete localStorage[configkey(myid)];
                    removesoul && delete localStorage[startkey(myid)];
                    removesoul && delete localStorage[updatekey(myid)];
                    var e = $.Event('storage');
                    e.originalEvent = {
                        key: configkey(e.id),
                        newValue: null
                    };
                    $(window).trigger(e);
                }
            };

            var configids = function() {
                return Object.keys(localStorage).filter(function(k) {
                    return isconfigkey(k);
                }).map(function(k) {
                    var id = k.replace(CONFIGPREFIX, '');
                    return {
                        config: id == myid ? config() :
                            JSON.parse(localStorage[k]),
                        id: id
                    };
                });
            };

            var getconfigs = function() {
                var configs = configids().map(function(cid) {
                    return cid.config;
                });

                return JSON.stringify(configs);
            };

            var trylongpoll = function() {
                if (new Date().getTime() > safestarttime) {
                    if (!longpoll) {

                        var strconfigs = getconfigs();

                        longpoll = $.ajax('/api/_listen', {
                            type: 'post',
                            data: strconfigs
                        });

                        $.when(longpoll).done(function(rsp) {
                            longpoll = null;
                            if (rsp != '[]') {
                                rsparr = JSON.parse(rsp);
                                rsparr.forEach(function(i) {
                                    var rsp = i.mtime;
                                    var rsptime = new Date().getTime();

                                    var dstid = configids()[i.i].id;
                                    localStorage[
                                        responsekey(dstid)] =
                                        rsp;
                                    localStorage[
                                        responsetimekey(dstid)] =
                                        rsptime;

                                    if (dstid == myid) {
                                        onbreak(rsptime, rsp);
                                    }
                                });
                            }
                            trylongpoll();
                        }).fail(function() {
                            clearstate();
                            safestarttime = new Date().getTime() + 1000;
                        });
                    }
                }
            };

            var gettimesummary = function() {
                var timesummary = [];
                if (SUMMARYLASTUPDATEKEY in localStorage &&
                    SUMMARYKEY in localStorage &&
                    parseInt(localStorage[SUMMARYLASTUPDATEKEY]) >
                        new Date().getTime() - MAX_SUMMARY_AGE
                ) {
                    timesummary = JSON.parse(localStorage[SUMMARYKEY]);
                } else {
                    var getids = function(prefix) {
                        return Object.keys(localStorage).filter(
                            function(k) {
                                return new RegExp(prefix + '[0-9]+')
                                    .test(k);
                            }).map(function(k) {
                                return k.replace(prefix, '');
                            });
                        };

                    var ids = Array.prototype.concat.apply([], [
                        getids(STARTPREFIX),
                        getids(LASTUPDATEPREFIX),
                        getids(CONFIGPREFIX),
                        getids(RESPONSEPREFIX),
                        getids(RESPONSETIMEPREFIX)
                    ]);

                    var uniqids = [];
                    ids.forEach(function(id) {
                        !uniqids.some(function(x) { return x == id }) &&
                            uniqids.push(id);
                    });

                    timesummary = uniqids.map(function(id) {
                        var startage = agefunc(startkey(id));
                        var updateage = agefunc(updatekey(id));
                        return {
                            id: id,
                            startage: startage,
                            updateage: updateage
                        };
                    }).sort(function(a, b) {
                        return b.startage - a.startage;
                    });

                    localStorage[SUMMARYLASTUPDATEKEY] =
                        new Date().getTime();
                    localStorage[SUMMARYKEY] =
                        JSON.stringify(timesummary);
                }
                return timesummary;
            };

            var getoldest = function() {
                var ret = gettimesummary();
                return ret[0];
            };

            var performanalysis = function() {
                var curtime = (new Date()).getTime();

                localStorage[startkey(myid)] = starttime;
                localStorage[updatekey(myid)] = curtime;
                if (config) {
                    localStorage[configkey(myid)] =
                        JSON.stringify(config());
                }

                // Remove broken stuff
                gettimesummary().filter(function(e) {
                    return e.startage == null || e.updateage == null;
                }).forEach(function(e) {
                    delete localStorage[startkey(e.id)];
                    delete localStorage[updatekey(e.id)];
                    delete localStorage[configkey(e.id)];
                    delete localStorage[responsekey(e.id)];
                    delete localStorage[responsetimekey(e.id)];
                    var e = $.Event('storage');
                    e.originalEvent = {
                        key: configkey(e.id),
                        newValue: null
                    };
                    $(window).trigger(e);
                });

                // Remove old stuff that isn't broken
                gettimesummary().filter(function(e) {
                    return e.updateage > MAX_AGE;
                }).forEach(function(e) {
                    delete localStorage[startkey(e.id)];
                    delete localStorage[updatekey(e.id)];
                    delete localStorage[configkey(e.id)];
                    delete localStorage[responsekey(e.id)];
                    delete localStorage[responsetimekey(e.id)];
                    var e = $.Event('storage');
                    e.originalEvent = {
                        key: configkey(e.id),
                        newValue: null
                    };
                    $(window).trigger(e);
                });

                var oldest = getoldest();

                var leaderage = agefunc(updatekey(oldest.id));

                if (parseInt(oldest.id) == myid) {
                    trylongpoll();
                } else {
                    if (longpoll) {
                        clearstate();
                    }
                    if (leaderage > MAX_AGE) {
                        clearstate(true);
                    }
                }
            };

            $(window).bind('storage', function(e) {
                if (e.originalEvent.key == responsetimekey(myid)) {
                    onbreak(localStorage[responsetimekey(myid)],
                        e.originalEvent.newValue);
                    performanalysis();
                }

                if (isconfigkey(e.originalEvent.key, true)) {
                    var oldest = getoldest();
                    if (parseInt(oldest.id) == myid) {
                        if (e.originalEvent.oldValue !==
                            e.originalEvent.newValue) {
                            var configs = getconfigs();
                            if (localStorage[LASTCONFIGSKEY] != configs) {
                                localStorage[LASTCONFIGSKEY] = configs;
                                if (longpoll) {
                                    longpoll.abort();
                                    longpoll = null;
                                    trylongpoll();
                                }
                            }
                        }
                    }
                }
            });

            var interval = setInterval(performanalysis, ANALYZE_INTERVAL);

            return {
                abort: function() {
                    clearstate(true);
                    clearInterval(interval);
                },
                ismine: function(id) { return myid == id; }
            };
        };

        return longpollmux(onbreak, config);
    };

    u.listen = function(onsuccess, listenconfigs) {

        var abort = false;

        var listen = function() {
            var xhr = $.ajax('/api/_listen', {
                type: 'post',
                contentType: 'application/json; charset=utf-8',
                dataType: 'json',
                data: JSON.stringify(listenconfigs)
            });

            $.when(xhr).done(function(res) {
                if (res != 'no events. retry') {
                    onsuccess();
                }

                if (!abort) {
                    listen();
                }
            }).fail(function() {
                xhr.abort();
                if (!abort) {
                    setTimeout(listen, 5000);
                }
            });

            return function() {
                abort = true;
                xhr.abort();
            };
        };

        return listen();
    };

})(this);
