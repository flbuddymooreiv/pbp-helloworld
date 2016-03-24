drop view if exists view_user_tables;
create or replace view view_user_tables as
    (select table_name
        from information_schema.tables
        where table_schema = 'public'
            and table_type = 'BASE TABLE'
            and table_name != 'table_mtime');
