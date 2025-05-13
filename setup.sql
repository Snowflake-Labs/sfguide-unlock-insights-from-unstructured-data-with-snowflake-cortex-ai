-- Set role context
USE ROLE accountadmin;

-- Enable Cortex Cross Region Inference
ALTER ACCOUNT SET CORTEX_ENABLED_CROSS_REGION = 'ANY_REGION';

-- Set role context
USE ROLE syadmin;

-- Set Environment Name
SET var_name = 'ai209';

-- Generate Environment Identifiers
SET var_warehouse_name = $var_name||'_wh';
SET var_database_name = $var_name||'_db';
SET var_schema_name = $var_name||'_db.demo';

-- Set Warehouse Context
CREATE WAREHOUSE IF NOT EXISTS IDENTIFIER($var_warehouse_name) WITH
    WAREHOUSE_SIZE = xsmall
    AUTO_SUSPEND = 60
    INITIALLY_SUSPENDED = true;
USE WAREHOUSE IDENTIFIER($var_warehouse_name);

-- Set Database Schema Context
CREATE DATABASE IF NOT EXISTS IDENTIFIER($var_database_name);
CREATE SCHEMA IF NOT EXISTS IDENTIFIER($var_schema_name);
USE SCHEMA IDENTIFIER($var_schema_name);
    
-- Create Images Stage
CREATE STAGE IF NOT EXISTS images_stage
    DIRECTORY = ( ENABLE = true )
    ENCRYPTION = ( TYPE = 'SNOWFLAKE_SSE' );
