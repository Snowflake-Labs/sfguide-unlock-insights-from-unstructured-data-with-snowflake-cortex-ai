<!--
summary: Unlock Insights from Unstructured Data with Snowflake Cortex AI
id: unlock_insights_from_unstructured_data_with_snowflake_cortex_ai
categories: data-engineering,ai,app-development
environments: web
status: Published
feedback link: https://github.com/Snowflake-Labs/sfguides/issues
tags: Snowflake Cortex, Generative AI, Streamlit, Snowflake, Data Applications, Multimodal AI
author: Sean Morris, Stephen Dickson
[environment_name]: ai209
-->

# Unlock Insights from Unstructured Data with Snowflake Cortex AI
<!-- ------------------------ -->
## Overview

Duration: 5

This guide demonstrates how to create a Streamlit application running inside Snowflake that unlocks insights from unstructured data using **Snowflake Cortex AI**.  
It shows how to translate, summarize, classify text, generate emails, and even analyze images — all without deploying external infrastructure.

### Prerequisites
- Snowflake account
- ACCOUNTADMIN role

### What You’ll Learn
- How to create a database, schema, and stage in Snowflake
- How to store unstructured data in Snowflake stages
- How to use SQL to run LLM functions (`TRANSLATE`, `SENTIMENT`, `SUMMARIZE`, `COMPLETE`)
- How to build a frontend application with Streamlit inside Snowflake

### What You'll Build
A fully functioning **Streamlit app** inside Snowflake that:
- Translates between multiple languages
- Scores sentiment of call transcripts
- Summarizes long-form text
- Classifies customer service inquiries
- Analyzes uploaded images using multimodal LLMs

<!-- ------------------------ -->
## Setup

Duration: 5

### Login to Snowsight

Log into Snowflake's web interface [Snowsight](https://docs.snowflake.com/en/user-guide/ui-snowsight.html#) using your Snowflake credentials.

### Enable Cross-Region Inference

In the Snowsight UI on the left hand sidebar, select the **Projects > Worksheets** tab.

In the top right hand corner, click the **+** button to create a new SQL worksheet.

Run the following SQL commands to [enable cortex cross-region inference](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cross-region-inference.html).

```sql
-- set role context
USE ROLE accountadmin;

-- enable Cortex Cross Region Inference
ALTER ACCOUNT SET CORTEX_ENABLED_CROSS_REGION = 'ANY_REGION';
```

### Create Snowflake Objects

In the same SQL worksheet, run the following SQL commands to create the [warehouse](https://docs.snowflake.com/en/sql-reference/sql/create-warehouse.html), [database](https://docs.snowflake.com/en/sql-reference/sql/create-database.html), [schema](https://docs.snowflake.com/en/sql-reference/sql/create-schema.html), and [stage](https://docs.snowflake.com/en/sql-reference/sql/create-stage.html)

> IMPORTANT:
> - If you use different names for objects created in this section, be sure to update scripts and code in the following sections accordingly.

```sql
-- Set role context
USE ROLE sysdmin;

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
```

### Download Images

Download sample [images](https://github.com/Snowflake-Labs/sfguide-unlock-insights-from-unstructured-data-with-snowflake-cortex-ai/tree/main/images).

### Upload Images

In the Snowsight UI on the left hand sidebar, select the **Data > Databases** tab and navigate to **AI209_DB > PUBLIC > STAGES > IMAGES_STAGE**.

In the top right hand corner, click **+ Files** to upload files to the stage.

Navigate back to the SQL worksheet and run the following SQL commands to verify the files have been uploaded:

<!-- ------------------------ -->
## Build Streamlit Application

Duration: 5

Let's create a Streamlit application for interactive image analysis:

### Setting Up the Streamlit App

To create and configure your Streamlit application in Snowflake:

1. Navigate to Streamlit in Snowflake:
   * Click on the **Streamlit** tab in the left navigation pane
   * Click on **+ Streamlit App** button in the top right

2. Configure App Settings:
   * Enter a name for your app (e.g., "AI/ML Toolkit")
   * Select the warehouse **AI209_WH**
   * Choose **AI209_DB.PUBLIC** as your database and schema
   * Click **Create**

3. Create the app:
   * In the editor, paste the complete code provided in the [streamlit_app.py](https://github.com/Snowflake-Labs/sfguide-unlock-insights-from-unstructured-data-with-snowflake-cortex-ai/blob/main/streamlit_app.py) file
   * Click "Run" to launch your application

The application provides:
- Translation: Translate text between 14 different languages using Snowflake Cortex
- Sentiment Analysis: Analyze the sentiment of call transcripts
- Data Summarization: Generate concise summaries of large text datasets
- Next Best Action: Use foundation models to identify customer next actions
- Text Classification: Categorize text into predefined categories
- Email Generation: Create customer emails based on call transcripts
- Question Answering: Ask questions to foundation models
- Multi-Modal Image Analysis: Analyze and categorize images using multi-modal models

<!-- ------------------------ -->
## Conclusion And Resources

Duration: 5

Congratulations! You've successfully built an end-to-end image analysis application using AI models via Snowflake Cortex. This solution allows you to extract valuable insights from images, detect emotions, analyze scenes, and generate rich descriptions - all within the Snowflake environment.

To continue your learning journey, explore creating more advanced prompting techniques, building domain-specific image analysis systems, or integrating this capability with other Snowflake data workflows.

### What You Learned
- How to set up Snowflake for image storage and processing
- How to use AI models like Claude 3.5 Sonnet and Pixtral-large for multimodal analysis
- How to create custom prompts for specialized image analysis
- How to build a Streamlit application for interactive image analysis
- How to implement batch processing for multiple images

### Related Resources
- [Snowflake Cortex Documentation](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-llm-rest-api)
- [Anthropic Tool Use on Snowflake Cortex Quickstart](https://quickstarts.snowflake.com/guide/getting-started-with-tool-use-on-cortex-and-anthropic-claude/index.html?index=..%2F..index#0)
- [Anthropic RAG on Snowflake Cortex Quickstart](https://quickstarts.snowflake.com/guide/getting_started_with_anthropic_on_snowflake_cortex/index.html?index=..%2F..index#0)
