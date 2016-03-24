(function() {
    'use strict';
    var apiurl = '/api/testtype';

    var val = $('<input>', { type: 'text' });
    $('body').append(val);

    $('body').append($('<button>').append('Add').click(function() {
        $.ajax({ url: apiurl, type: 'POST', data: { val: val.val() } });
    }));

    var results = $('<div>');
    $('body').append(results);

    var triggerget = function(successfunc) {
        $.ajax({ url: apiurl, success: successfunc});
    };

    var listenerstarted = false;
    var refreshResults = function(r) {
        var items = JSON.parse(r);
        results.empty();
        results.append(
            items.map(function(i) {
                return $('<div>').append(
                    i.id, ': ', i.val, 
                    $('<button>').append('delete')
                        .click(function() {
                            $.ajax({
                                url: apiurl,
                                type: 'DELETE',
                                data: { id: i.id }
                            });
                            $(this).parent().remove();
                        })
                );
            })
        );

        if(!listenerstarted) {
            var onsuccess = function(rsp) {
                triggerget(refreshResults);
            };

            listen.start(onsuccess);
            listenerstarted = true;
        }
    };

    triggerget(refreshResults);
})();
