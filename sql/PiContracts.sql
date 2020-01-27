CREATE TABLE public.PiContracts
(	"market_id" REFERENCES PiMarkets(market_id),
    "contract_id" integer NOT NULL,
    "update_ts" timestamp without time zone,
    "predictit_ts" timestamp without time zone,
    "market" character varying(75),
    "end_date" timestamp without time zone,
    "url" character varying(200),
    "rules" text,
    "baseline" integer,
    PRIMARY KEY ("market_id", "contract_id", "update_ts")
);

ALTER TABLE public.PiContracts
    OWNER to postgres;