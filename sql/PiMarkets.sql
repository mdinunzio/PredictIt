CREATE TABLE public.PiMarkets
(
    "market_id" integer NOT NULL,
    "update_ts" timestamp without time zone,
    "market" character varying(75),
    "end_date" timestamp without time zone,
    "url" character varying(200),
    PRIMARY KEY ("market_id")
);

ALTER TABLE public.PiMarkets
    OWNER to postgres;