CREATE TABLE public.piContracts
(	"marketId" REFERENCES piMarkets(marketId),
    "contractId" integer NOT NULL,
    "updateTs" timestamp without time zone,
    "market" character varying(75),
    "endDate" timestamp without time zone,
    "url" character varying(200),
    PRIMARY KEY ("marketId", "contractId", "updateTs")
);

ALTER TABLE public.piContracts
    OWNER to postgres;