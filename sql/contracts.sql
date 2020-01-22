CREATE TABLE public.contracts
(	"marketId" REFERENCES markets(marketId),
    "contractId" integer NOT NULL,
    "updateTs" timestamp without time zone,
    "market" character varying(75),
    "endDate" timestamp without time zone,
    "url" character varying(200),
    PRIMARY KEY ("marketId", "contractId", "updateTs")
);

ALTER TABLE public.markets
    OWNER to postgres;