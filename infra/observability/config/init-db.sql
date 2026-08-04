-- LAOS observability — bootstrap databases for Langfuse + LiteLLM
-- Mounted at /docker-entrypoint-initdb.d/ on the postgres container.

-- LiteLLM needs its own database + credentials for Prisma migrations.
DO $$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'litellm') THEN
      CREATE ROLE litellm LOGIN PASSWORD 'litellm';
   END IF;
END
$$;

SELECT 'CREATE DATABASE litellm OWNER litellm'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'litellm')
\gexec

-- Langfuse already provisioned via POSTGRES_USER/POSTGRES_DB env vars.
