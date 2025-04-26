import label_studio_sdk

def export_annotations(project_id: int, output_dir: str):
    """Export Label Studio annotations for model training."""
    ls = label_studio_sdk.Client(url="http://localhost:8080", api_key="YOUR_KEY")
    project = ls.get_project(id=project_id)
    project.export_tasks(output_dir=output_dir)