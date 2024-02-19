# PostgreSQL + pgvector

[pgvector](https://github.com/pgvector/pgvector) is an open-source vector similarity search for Postgres

Store your vectors with the rest of your data. Supports:

- exact and approximate nearest neighbor search
- L2 distance, inner product, and cosine distance
- any language with a Postgres client

Plus ACID compliance, point-in-time recovery, JOINs, and all of the other great features of Postgres.

## Container image

The `Containerfile` builds a PostgreSQL 15 + pgvector image (pgvector is built from source).
You can then deploy this container as any other PostgreSQL image.

A prebuilt image is available at [https://quay.io/repository/rh-aiservices-bu/postgresql-15-pgvector-c9s](https://quay.io/repository/rh-aiservices-bu/postgresql-15-pgvector-c9s).

## Deployment

You can easily deploy a PostgreSQL+pgvector instance with the provided files (namespace is not mentioned in the files, so make sure you use them in the right one):

- `01_db_secret.yaml`: the secret that will define the database name as well as the user name and password to connect to it.
- `02_pvc.yaml`: an example of PVC needed to persist the database. If you don't have a default storage class you must add it.
- `03_deployment.yaml`: deployment of PostgreSQL server.
- `04_services.yaml`: service to expose the PostgreSQL server.

After applying all those files you should have a running PostgreSQL+pgvector server running, accessible at `postgresql.your-project.svc.cluster.local:5432`

The PgVector extension must be manually enabled in the server. This can only be done as a Superuser (above account won't work). The easiest way is to:

- Connect to the running server Pod, either through the Terminal view in the OpenShift Console, or through the CLI with: `oc rsh services/postgresql`
- Once connected, enter the following command:

`psql -d vectordb -c "CREATE EXTENSION vector;"`

(adapt the command if you changed the name of the database in the Secret).
If the command succeeds, it will print `CREATE EXTENSION`.

- Exit the terminal

Your vector database is now ready to use! Head to the [notebooks section](../examples/notebooks/) for examples on how to use it.
