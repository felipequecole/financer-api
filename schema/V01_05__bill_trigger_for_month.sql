CREATE OR REPLACE FUNCTION notify_month_update_after_bill_update()
    RETURNS TRIGGER
    LANGUAGE PLPGSQL
AS
$$
BEGIN
    IF NEW.id is null then
        PERFORM pg_notify('month', concat_ws(' ', 'add', OLD.month_id)) ;
    ELSE
        PERFORM pg_notify('month', concat_ws(' ', 'add', NEW.month_id)) ;
    end if;
    RETURN NEW;
END
$$;

CREATE OR REPLACE TRIGGER notify_month_update_for_bill
    AFTER INSERT OR UPDATE OR DELETE
    ON bills
    FOR EACH ROW
execute FUNCTION notify_month_update_after_bill_update();
