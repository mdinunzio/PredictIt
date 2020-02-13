CREATE TABLE public.pitweetmeta
(
	"market_id" integer NOT NULL,
	"update_ts" timestamp without time zone NOT NULL,
	"user" character varying(25),
	"baseline" bigint,
	"market_name" character varying(200),
	"market_open_ts" timestamp without time zone,
	"market_end_ts" timestamp without time zone,
	"rule" text,
    FOREIGN KEY ("market_id", "update_ts") REFERENCES pimarketmeta("market_id", "update_ts")
);

ALTER TABLE public.pitweetmeta
    OWNER to postgres;