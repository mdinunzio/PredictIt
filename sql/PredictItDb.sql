-- Database: PredictItAnalytics

-- DROP DATABASE "PredictItAnalytics";

CREATE DATABASE "PredictItAnalytics"
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'English_United States.1252'
    LC_CTYPE = 'English_United States.1252'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

COMMENT ON DATABASE "PredictItAnalytics"
    IS 'A database to contain PredictIt.org information.';