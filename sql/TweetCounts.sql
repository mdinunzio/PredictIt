CREATE TABLE public.TweetCounts
(
    "user" character varying(25),
    "update_ts" timestamp without time zone,
    "tweets" bigint,
    PRIMARY KEY ("user", "update_ts")
);

ALTER TABLE public.TweetCounts
    OWNER to postgres;