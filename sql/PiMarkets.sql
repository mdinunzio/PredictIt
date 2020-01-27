CREATE TABLE public.PiMarkets
(
    "market_id" integer NOT NULL,
    "name" character varying(150),
    "short_name" character varying(125),
    "end_date" timestamp without time zone,
    "url" character varying(200),
    "status" character varying(20),
    "predictit_ts" timestamp without time zone,
    "update_ts" timestamp without time zone,
    PRIMARY KEY ("market_id")
);

ALTER TABLE public.PiMarkets
    OWNER to postgres;