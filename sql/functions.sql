CREATE OR REPLACE FUNCTION notify_on_modify_func() RETURNS TRIGGER AS $body$
DECLARE
    v_old_data TEXT;
    v_new_data TEXT;
BEGIN
    IF (TG_OP = 'UPDATE') THEN
        v_old_data := to_json(OLD.*)::text;
        v_new_data := to_json(NEW.*)::text;
        perform pg_notify(
            TG_TABLE_NAME::TEXT || '_update', '{ "old": ' || v_old_data || ', "new": ' || v_new_data || '}');
        return new;
    ELSIF (TG_OP = 'DELETE') THEN
        v_old_data := to_json(OLD.*)::text;
        perform pg_notify(
            TG_TABLE_NAME::TEXT || '_delete', v_old_data);
        return old;
    ELSIF (TG_OP = 'INSERT') THEN
        v_new_data := to_json(NEW.*)::text;
        perform pg_notify(
            TG_TABLE_NAME::TEXT || '_insert', v_new_data);
        return new;
    ELSE
        raise warning '[notify_on_modify_func] - Other action occurred: %, at %', TG_OP, now();
        RETURN NULL;
    END IF;

EXCEPTION
    WHEN data_exception THEN
        raise warning '[notify_on_modify_func] - UDF ERROR [DATA EXCEPTION] - SQLSTATE: %, SQLERRM: %, TABLE: %', SQLSTATE, SQLERRM, TG_TABLE_NAME::TEXT;
        RETURN NULL;
    WHEN unique_violation THEN
        raise warning '[notify_on_modify_func] - UDF ERROR [UNIQUE] - SQLSTATE: %, SQLERRM: %, TABLE: %', SQLSTATE, SQLERRM, TG_TABLE_NAME::TEXT;
        RETURN NULL;
    WHEN OTHERS THEN
        raise warning '[notify_on_modify_func] - UDF ERROR [OTHER] - SQLSTATE: %, SQLERRM: %, TABLE: %', SQLSTATE, SQLERRM, TG_TABLE_NAME::TEXT;
        RETURN NULL;
END;
$body$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION update_mtime_column()
RETURNS TRIGGER AS $$
DECLARE
    currtime timestamp;
BEGIN
   currtime := now();
   delete from table_mtime where name = TG_TABLE_NAME;
   insert into table_mtime (name, mtime) values (TG_TABLE_NAME, currtime);

   IF (TG_OP = 'INSERT') THEN
      RETURN NEW;
   ELSIF (TG_OP = 'UPDATE') THEN
       IF row(NEW.*) IS DISTINCT FROM row(OLD.*) THEN
          NEW.mtime = currtime; 
          RETURN NEW;
       ELSE
          RETURN OLD;
       END IF;
   ELSIF (TG_OP = 'DELETE') THEN
      RETURN OLD;
   END IF;
END;
$$ language 'plpgsql';
