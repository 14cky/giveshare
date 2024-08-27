import os

project_dir = 'path/to/your/project'

for root, dirs, files in os.walk(project_dir):
    for file in files:
        if file.endswith('.py') and file != '__init__.py' and 'migrations' in root:
            file_path = os.path.join(root, file)
            print(f"Deleting {file_path}")
            os.remove(file_path)
        elif file.endswith('.pyc') and 'migrations' in root:
            file_path = os.path.join(root, file)
            print(f"Deleting {file_path}")
            os.remove(file_path)
