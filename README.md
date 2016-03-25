This is a [hello world](https://en.wikipedia.org/wiki/%22Hello,_World!%22_program) for the Python-Bottle-PostgreSQL (**PBP**) design pattern. 

This is not a globally scaleable distributed next-best-thing... Yet.

By setting up this project, you will be able to insert/update/delete rows in a PostgreSQL table via any connection and those changes will propagate **immediately** to a browser over a simple ReST interface, to a very simple UI.

This is just an evolving reference implementation of the goal above with an architecture that avoids cultural lock-in (Django, RoR, meteor, etc.).

You may notice the use of uWSGI later on but that it is not in the title here. The uWSGI is somewhat interchangeable in this architecture, so it doesn't get included. Be advised, however: In a pure Python WSGI environment, all requests are synchronous. uWSGI helps us currently by running our uWSGI stack with one thread per request, but in the future, we can accomplish many asynchronous requests per thread by using `uwsgi.wait_fd_read`, vastly increasing the number of concurrent clients we can service.

## Features:

* Small
* Scaleable 
* Mature dependencies 
* Portable
* Multi-Threaded
* Long Poll Push Notifications

## TODO/Known Issues:

* Replicate the model client-side for more sensible client behavior
* Make the web interface asynchronous with `uwsgi.wait_fd_read`
* Make the database interface asynchronous/scale better:
    * Use fewer database connections and mux them similar to the way the browser muxes one connection for its notify channel to the server

This configuration is most strongly tested on Debian 8. It is highly recommended that be the distribution to use.

## Design

Python accepts HTTP requests with its built in **WSGI** stack. These **WSGI** requests are passed to python **bottle** to help register routing and manage request/response headers and cookies and query strings. The requests are routed *however* you wish, but an example data type `testtype` is included to illustrate where SQL tables should be added and facilitate the creation of a **ReST** API. It is on the user tables (like `testtype`) in the PostgreSQL database that we install `mtime` columns for row-level subscription granularity and a table-level subscription granularity. A simple UI is included in `./pages/index.py` and `./static/js/index.js` to drive the **ReST** interface and show how a UI should interact with the server to produce an environment whereby an **insert/update/delete in the database will cause an update on the UI**. Because browsers are limited by how many connections they can open to one server, to support distribution of changes to multiple tabs, the browser's site **localStorage** is used to propagate event information from one master listener tab to other subscriber tabs, the master being auto-negotiated and self-healing within the browser if the master suddenly disappears or new tabs join in.

**Any and all of these components are subject to change**, so don't interpret this project as an authoritative reference on anything: web, python, concurrent programming, etc. It is merely to illustrate *a* way to accomplish a few technical objectives that can allow the implementation of a fairly scaleable (hundreds of users) system while staying as commercially inexpensive as possible (free), and keeping to a minimal integration of existing, mature, widely-supported technologies, protocols, and patterns.

## Install Dependencies:

    sudo apt-get update
    sudo apt-get install git
    sudo apt-get install postgresql
    sudo apt-get install python3-bottle
    sudo apt-get install python3-psycopg2
    sudo apt-get install python3-dateutil
    sudo apt-get install uwsgi
    sudo apt-get install uwsgi-plugin-python3

## Configure:

    * /etc/hosts:
        127.0.0.1        thehostname localhost
        1.2.3.4          thehostname.domain.com

    * /etc/postgresql/9.4/main/pg_hba.conf:
      Ensure only this line exists:
        local   all     all                             trust

    * /etc/postgresql/9.4/main/postgresql.conf:
        max_connections = 512

    * Restart postgresql:
        sudo service postgresql restart

    * Assign a secure password to the postgres user:
        * Run 'psql -U postgres'
        * Run:
            ALTER USER postgres PASSWORD '!ultralongunguessablepassword!';
        * Ctrl+D out

    * Enable services at boot:
        sudo update-rc.d postgresql enable
        
    * Reboot:
        sudo shutdown -r now

## Initializing the Database

    ./sql/reinitdb.sh helloworld

## Running the Site

    To run threaded:
        PYTHONPATH=. uwsgi \
            --plugins python34,ugreen -w run:app --socket :8888 \
            --protocol http --threads 2000 
    To run async (not supported yet):
        PYTHONPATH=. uwsgi \
            --plugins python34,ugreen -w run:app --socket :8888 \
            --protocol http --async 10000
