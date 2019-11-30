-- Initial schema for PostgreSQL.

CREATE TYPE currency_type AS ENUM (
  'USD',
  'UAH',
  'RUB'
  -- other currency
);

CREATE TABLE account (
    id               serial PRIMARY KEY NOT NULL,
    name             varchar(512) UNIQUE NOT NULL,
    balance          numeric(9, 2) NOT NULL CHECK (balance >= 0), -- or money data type
    currency         currency_type NOT NULL,
    created_at       timestamp NOT NULL DEFAULT NOW()
);

CREATE INDEX CONCURRENTLY idx_account_name on account (name);
CREATE INDEX CONCURRENTLY idx_account_created_at_brin ON account USING brin(created_at);


CREATE TYPE direction_type AS ENUM (
  'outgoing',
  'incoming'
);

CREATE TABLE payment (
    id               serial NOT NULL,
    account_id       bigint NOT NULL REFERENCES account (id),
    to_account_id    bigint NOT NULL REFERENCES account (id),
    amount           numeric(9, 2) NOT NULL CHECK (amount > 0),
    direction        direction_type NOT NULL,
    created_at       timestamp NOT NULL DEFAULT NOW()
) PARTITION BY RANGE (created_at);

CREATE INDEX idx_payment_created_at_brin ON payment USING brin(created_at);


-- Function for creating partitions, you can run it when you will need more partition.
-- We do not create partitions automatically because it will increase cost for insertion time,
-- so you need to do it manually or by periodic task.
CREATE OR REPLACE FUNCTION create_partitions(table_name text, day date) RETURNS VOID AS
$BODY$
DECLARE
    sql text;
BEGIN
  select format(
    'CREATE TABLE %s_%s PARTITION OF %s FOR VALUES FROM (''%s'') TO (''%s'')', 
    table_name, 
    (replace(day::text, '-', '_')), 
    table_name, 
    day, 
    (day + INTERVAL '1 MONTH')::date
  ) into sql;
  EXECUTE sql;
END;
$BODY$
LANGUAGE plpgsql;

-- Create partitions for table payment from now to 1 YEAR in future over each month.
SELECT create_partitions('payment', day::date) FROM generate_series
  (date_trunc('month', current_date), current_date + INTERVAL '1 YEAR', '1 MONTH'::interval) day;
