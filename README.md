This is a "hello world" for the Python-Bottle-PostgreSQL (PBP) design pattern.
This is not a globally scaleable distributed next-best-thing
This is just an evolving reference implementation of an architecture that avoids cultural lock-in (Django, RoR, meteor, etc.).

Features:
    Small
    Scaleable 
    Mature libraries 
    Portable 
    Multi-Threaded
    Long Poll Push Notifications

TODO/Known Issues:
    Replicate the model client-side for more sensible client behavior
    Make the web interface asynchronous with uwsgi wait_fd_read
    Make the database interface asynchronous/scale better:
        * Use fewer database connections and mux them similar to the way the
          browser muxes one connection for its notify channel to the server

This configuration is most strongly tested on Debian 8. It is highly
recommended that be the distribution to use.

Install:
    sudo apt-get update
    sudo apt-get install git
    sudo apt-get install postgresql
    sudo apt-get install python3-bottle
    sudo apt-get install python3-psycopg2
    sudo apt-get install python3-dateutil
    sudo apt-get install uwsgi
    sudo apt-get install uwsgi-plugin-python3

Configure:
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

Initializing the Database
    ./sql/reinitdb.sh helloworld

Running the Site
    To run threaded:
        PYTHONPATH=. uwsgi \
            --plugins python34,ugreen -w run:app --socket :8888 \
            --protocol http --threads 2000 
    To run async (not supported yet):
        PYTHONPATH=. uwsgi \
            --plugins python34,ugreen -w run:app --socket :8888 \
            --protocol http --async 10000
