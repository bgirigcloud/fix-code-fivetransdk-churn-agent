from fivetran_sdk.bigquery.connector import BigQueryConnector

def main():
    # IMPORTANT: Replace with your Google Cloud project ID.
    project_id = "your-gcp-project-id"

    # Initialize the connector
    connector = BigQueryConnector(project_id)

    # List datasets
    datasets = connector.list_datasets()

    # List tables in a specific dataset
    if datasets:
        # Replace with your dataset ID
        dataset_id = "your_dataset_id"
        try:
            connector.list_tables(dataset_id)
        except Exception as e:
            print(f"Could not list tables for dataset {dataset_id}. Please ensure it exists and you have permissions.")
            print(e)


if __name__ == "__main__":
    main()
