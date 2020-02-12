CREATE TABLE public.PiApi
(
	"id_market" integer NOT NULL,
	"name_market" character varying(150),
    "short_name_market" character varying(80),
    "image_market" character varying(150),
    "url" character varying(200),
    "status_market" character varying(10),
    "id_contract" integer NOT NULL,
    "date_end" timestamp without time zone,
    "image_contract" character varying(150),
    "name_contract" character varying(150),
    "short_name_contract" character varying(80),
    "status_contract" character varying(10),
    "last_trade_price" float,
    "best_buy_yes_cost" float,
    "best_buy_no_cost" float,
    "best_sell_yes_cost" float,
    "best_sell_no_cost" float,
    "last_close_price" float,
    "display_order" integer,
    "update_ts" timestamp without time zone,
    "predictit_ts" timestamp without time zone,
    PRIMARY KEY ("update_ts", "id_market", "id_contract")
);

ALTER TABLE public.PiApi
    OWNER to postgres;

CREATE INDEX  piapi_id_market_idx ON piapi
(id_market);
