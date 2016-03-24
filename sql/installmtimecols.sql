do 
$$ 
begin 
    execute(select 
        string_agg(
            'alter table ' || quote_ident(t.table_name) ||
            ' add column mtime timestamp default now();' ||
            'create index on ' || quote_ident(t.table_name) || 
            ' (mtime);' ||
            'drop trigger if exists _mtime_update on ' || 
                quote_ident(t.table_name) || ';' || 
            'create trigger _mtime_update ' ||
                ' before insert or update or delete on ' || 
                    quote_ident(t.table_name) || 
                ' for each row execute procedure update_mtime_column();', 
            E'\n')
        from (select table_name from view_user_tables) t); 
end 
$$;
