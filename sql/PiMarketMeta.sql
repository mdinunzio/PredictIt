CREATE TABLE public.pimarketmeta
(
	"market_id" integer NOT NULL,
	"update_ts" timestamp without time zone NOT NULL,
	"market_name" character varying(200),
	"image_name" character varying(150),
	"market_type" integer,
	"date_end_string" character varying(50),
	"is_active" boolean,
	"rule" text,
	"user_has_ownership" boolean,
	"user_has_trade_history" boolean,
	"user_investment" float,
	"user_max_payout" float,
	"info" character varying(150),
	"date_opened" timestamp without time zone,
	"is_market_watched" boolean,
	"seo_title" character varying(150),
	"seo_description" character varying(500),
	"market_url" character varying(150),
	"status" character varying(25),
	"is_open" boolean,
	"is_open_status_message" character varying(50),
	"is_trading_suspended" boolean,
	"is_trading_suspended_message" character varying(50),
	"is_engine_busy" boolean,
	"is_engine_busy_message" character varying(50),
	"disqus_identifier" character varying(50),
	"disqus_title" character varying(150),
	"disqus_user_auth" character varying(50),
	"disqus_url" character varying(150),
    PRIMARY KEY ("market_id", "update_ts")
);

ALTER TABLE public.pimarketmeta
    OWNER to postgres;