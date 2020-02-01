CREATE TABLE public.PiMarkets
(
    "market_id" integer NOT NULL,
    "name" character varying(150),
    "short_name" character varying(125),
    "image" character varying(200),
    "url" character varying(200),
    "update_ts" timestamp without time zone,
    PRIMARY KEY ("market_id")
);

ALTER TABLE public.PiMarkets
    OWNER to postgres;