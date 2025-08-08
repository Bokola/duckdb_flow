from ingestion.bigquery import (
    get_bigquery_client,
    get_bigquery_result,
    build_pypi_query,
)
from ingestion.duck import (
    create_table_from_dataframe,
    connect_to_md,
    write_to_md_from_duckdb,
    load_aws_credentials,
    write_to_s3_from_duckdb

)

import os

# pipeline params
from ingestion.models import PypiJobParameters, FileDownloads, validate_dataframe

# pass key-value parameters
import fire
import duckdb
from loguru import logger


# this is a pydantic model passed to our code
def main(params: PypiJobParameters):
    # os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (
    #     "/home/basil-owiti/.config/gcloud/data-engineering-468305-d5e118917ac1.json"
    # )

    # df = get_bigquery_result(
    #     build_pypi_query(), get_bigquery_client(params.gcp_project)
    # )

    df = get_bigquery_result(
        query_str=build_pypi_query(params),
        bigquery_client=get_bigquery_client(project_name=params.gcp_project),
    )

    # validate_dataframe(df, FileDownloads)

    # print("hello pipeline")
    print(df)

    # copy df using duckdb
    conn = duckdb.connect()
    conn.register("df", df)
    # conn.sql("select * from df limit 10")
    create_table_from_dataframe(conn, params.table_name, "df")
    # conn.sql(
    #     "COPY (SELECT * FROM df) TO 'duckdb.csv' (FORMAT csv, HEADER true, DELIMITER ',')"
    # )

    logger.info(f"sinking data to {params.destination}")
    if "local" in params.destination:
        conn.sql(f"COPY {params.table_name} TO '{params.table_name}.csv';")
    
    if "s3" in params.destination:
        # install extensions(conn, params.extensions)
        load_aws_credentials(conn, params.aws_profile)
        write_to_s3_from_duckdb(
            conn, f"{params.table_name}, params.s3_path", "timestamp"
        )
    
    if "md" in  params.destination:
        connect_to_md(conn, os.environ["motherduck_token"])
        write_to_md_from_duckdb(
            duckdb_con=conn,
            table = f"{params.table_name}",
            local_database="memory",
            remote_database="pypi",
            timestamp_column=params.timestamp_column,
            start_date=params.start_date,
            end_date=params.end_date
        )



if __name__ == "__main__":
    fire.Fire(lambda **kwargs: main(PypiJobParameters(**kwargs)))
