CREATE TABLE public.TweetCounts
(
	"update_ts" timestamp without time zone,
    "user" character varying(25),
    "tweets" bigint,
    PRIMARY KEY ("update_ts", "user")
);

ALTER TABLE public.TweetCounts
    OWNER to postgres;