CREATE TABLE public.markets
(
    "marketId" integer NOT NULL,
    "updateDate" date,
    "market" character varying(75),
    "endDate" timestamp without time zone,
    "url" character varying(200),
    PRIMARY KEY ("marketId")
);

ALTER TABLE public.markets
    OWNER to postgres;