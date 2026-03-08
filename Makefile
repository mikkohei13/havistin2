ENV_VARS := $(shell grep -v '^\#' .env | grep '=' | sed 's/ *\#.*//' | tr '\n' ',' | sed 's/,$$//')

dev:
	docker compose up --build; docker compose down

deploy:
	gcloud run deploy havistin2 --project=havistin --port=80 \
		--max-instances=4 --concurrency=10 --memory=1024Mi \
		--timeout=40 --source . \
		--set-env-vars="$(ENV_VARS)"
