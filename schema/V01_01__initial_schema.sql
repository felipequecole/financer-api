CREATE OR REPLACE FUNCTION gen_slug(year integer, month integer)
    RETURNS TEXT
    LANGUAGE PLPGSQL
    IMMUTABLE
    RETURNS NULL ON NULL INPUT
AS
$$
BEGIN
   RETURN coalesce(TO_CHAR(year, 'fm0000'), '')::TEXT || '_' || coalesce(TO_CHAR(month, 'fm00'), '')::TEXT;
END
$$;

CREATE TABLE public.expenses (
  id uuid PRIMARY KEY NOT NULL DEFAULT gen_random_uuid(),
  name CHARACTER VARYING NOT NULL,
  due_day INTEGER NOT NULL,
  amount NUMERIC NOT NULL DEFAULT 0,
  active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITHOUT TIME ZONE,
  active_until TIMESTAMP WITHOUT TIME ZONE
);
CREATE INDEX ix_expenses_id ON expenses USING BTREE (id);

CREATE TABLE public.months (
  id uuid PRIMARY KEY NOT NULL DEFAULT gen_random_uuid(),
  year INTEGER NOT NULL,
  month INTEGER NOT NULL,
  slug VARCHAR GENERATED ALWAYS AS ( gen_slug(year, month) ) STORED
);
CREATE UNIQUE INDEX unique_month ON months USING BTREE (slug);
CREATE INDEX ix_months_year ON months USING BTREE (year);
CREATE INDEX ix_months_id ON months USING BTREE (id);
CREATE INDEX ix_months_month ON months USING BTREE (month);


CREATE TABLE public.income (
  id uuid PRIMARY KEY NOT NULL DEFAULT gen_random_uuid(),
  name CHARACTER VARYING NOT NULL,
  month_id VARCHAR NOT NULL,
  amount NUMERIC NOT NULL DEFAULT 0,
  created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITHOUT TIME ZONE,
  FOREIGN KEY (month_id) REFERENCES public.months (slug)
  MATCH SIMPLE ON UPDATE NO ACTION ON DELETE CASCADE
);
CREATE INDEX ix_income_id ON income USING BTREE (id);

CREATE TABLE public.bills (
  id uuid PRIMARY KEY NOT NULL DEFAULT gen_random_uuid(),
  name CHARACTER VARYING NOT NULL,
  month_id VARCHAR NOT NULL,
  day INTEGER,
  amount NUMERIC NOT NULL,
  paid BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITHOUT TIME ZONE,
  paid_at TIMESTAMP WITHOUT TIME ZONE,
  FOREIGN KEY (month_id) REFERENCES public.months (slug)
  MATCH SIMPLE ON UPDATE NO ACTION ON DELETE CASCADE
);
CREATE INDEX ix_bills_id ON bills USING BTREE (id);
CREATE INDEX ix_bills_day ON bills USING BTREE (day);
