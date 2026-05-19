-- Create read-only user for Prometheus postgres_exporter
CREATE USER exporter WITH PASSWORD 'exporter_pass';
GRANT CONNECT ON DATABASE booking TO exporter;
GRANT pg_read_all_statistics TO exporter;

-- Grant SELECT on all existing tables in public schema
GRANT SELECT ON ALL TABLES IN SCHEMA public TO exporter;

-- Grant SELECT on future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO exporter;
