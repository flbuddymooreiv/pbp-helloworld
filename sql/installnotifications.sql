do 
$$ 
begin 
    execute(select 
        string_agg(
            'drop trigger if exists _notify on ' || 
                quote_ident(t.table_name) || ';' || 
            'create trigger _notify ' ||
                ' after insert or update or delete on ' || 
                    quote_ident(t.table_name) || 
                ' for each row execute procedure notify_on_modify_func();', E'\n') 
        from (select table_name from view_user_tables) t); 
end 
$$;
