-- Compatibility entrypoint; execute from the repository root in the mysql client.
-- Canonical schema and analytical views live in database/.
SOURCE database/schema.sql;
SOURCE database/views.sql;

