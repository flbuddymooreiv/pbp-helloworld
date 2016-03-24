create table table_mtime (
    name            text unique not null, 
    mtime           timestamp default now()
);

create table testtype (
    id              serial,
    val             text not null,
    primary key(id)
);
