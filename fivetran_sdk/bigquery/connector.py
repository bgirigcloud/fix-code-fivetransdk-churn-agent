from google.cloud import bigquery

class BigQueryConnector:
    def __init__(self, project_id):
        self.project_id = project_id
        self.client = bigquery.Client(project=project_id)

    def list_datasets(self):
        """Lists all datasets in the project."""
        datasets = list(self.client.list_datasets())
        project = self.client.project
        if datasets:
            print(f"Datasets in project {project}:")
            for dataset in datasets:
                print(f"\t{dataset.dataset_id}")
        else:
            print(f"{project} project does not contain any datasets.")
        return datasets

    def list_tables(self, dataset_id):
        """Lists all tables in a given dataset."""
        tables = self.client.list_tables(dataset_id)
        print(f"Tables in dataset {dataset_id}:")
        for table in tables:
            print(f"\t{table.table_id}")
        return tables

if __name__ == '__main__':
    # Replace with your project ID
    project_id = "your-gcp-project-id"
    connector = BigQueryConnector(project_id)
    connector.list_datasets()
