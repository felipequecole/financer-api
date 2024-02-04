CREATE VIEW v_month_details AS
SELECT months.*, total_income, total_expense, (total_income - total_expense) balance, first_date, last_date, paid
FROM months
         LEFT JOIN (SELECT month_id, SUM(amount) total_income
                    FROM income
                    GROUP BY month_id) inc ON inc.month_id = months.slug
         LEFT JOIN (SELECT month_id,
                           SUM(amount)       total_expense,
                           BOOL_AND(paid) as paid,
                           MIN(day)       as first_date,
                           MAX(day)       as last_date
                    FROM bills
                    GROUP BY month_id) exp ON exp.month_id = months.slug;

CREATE OR REPLACE FUNCTION notify_update_or_insert_expense()
    RETURNS TRIGGER
    LANGUAGE PLPGSQL
AS
$$
BEGIN
    IF NEW.id is null then
        PERFORM pg_notify('expenses', concat_ws(' ', 'del', OLD.id)) ;
    ELSE
        PERFORM pg_notify('expenses', concat_ws(' ', 'add', NEW.id)) ;
    end if;
    RETURN NEW;
END
$$;

CREATE OR REPLACE TRIGGER notify_expenses_updates
    AFTER INSERT OR UPDATE OR DELETE
    ON expenses
    FOR EACH ROW
execute FUNCTION notify_update_or_insert_expense();
