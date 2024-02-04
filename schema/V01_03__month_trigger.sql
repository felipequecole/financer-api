CREATE OR REPLACE FUNCTION notify_update_or_insert_month()
    RETURNS TRIGGER
    LANGUAGE PLPGSQL
AS
$$
BEGIN
    IF NEW.id is null then
        PERFORM pg_notify('month', concat_ws(' ', 'del', OLD.slug)) ;
    ELSE
        PERFORM pg_notify('month', concat_ws(' ', 'add', NEW.slug)) ;
    end if;
    RETURN NEW;
END
$$;

CREATE OR REPLACE TRIGGER notify_month_update
    AFTER INSERT OR UPDATE OR DELETE
    ON months
    FOR EACH ROW
execute FUNCTION notify_update_or_insert_month();
