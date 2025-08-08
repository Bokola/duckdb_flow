include .env
export

.PHONY: pypi-ingest format
pypi-ingest:
	poetry run python -m ingestion.pipeline \
	--start_date $$START_DATE \
	--end_date $$END_DATE \
	--pypi_project $$PYPI_PROJECT \
	--table_name $$TABLE_NAME \
	--s3_path $$S3_PATH \
	--aws_profile $$AWS_PROFILE \
	--gcp_project $$GCP_PROJECT \
	--timestamp_column $$TIMESTAMP_COLUMN \
	--destination $$DESTINATION

# use ruff to farmat tree
format:
	ruff format .
test:
	pytest tests