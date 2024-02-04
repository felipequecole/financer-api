CREATE OR REPLACE FUNCTION notify_update_or_insert_bill()
    RETURNS TRIGGER
    LANGUAGE PLPGSQL
AS
$$
BEGIN
    IF NEW.id is null then
        PERFORM pg_notify(concat_ws('_', 'bill', OLD.month_id), concat_ws(' ', 'del', OLD.id));
    ELSE
        PERFORM pg_notify(concat_ws('_', 'bill', NEW.month_id), concat_ws(' ', 'add', NEW.id));
    end if;
    RETURN NEW;
END
$$;

CREATE OR REPLACE TRIGGER notify_bill_update
    AFTER INSERT OR UPDATE OR DELETE
    ON bills
    FOR EACH ROW
execute FUNCTION notify_update_or_insert_bill();
