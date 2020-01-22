CREATE TABLE public.piMarkets
(
    "marketId" integer NOT NULL,
    "updateTs" timestamp without time zone,
    "market" character varying(75),
    "endDate" timestamp without time zone,
    "url" character varying(200),
    PRIMARY KEY ("marketId")
);

ALTER TABLE public.piMarkets
    OWNER to postgres;