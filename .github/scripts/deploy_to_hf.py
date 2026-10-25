from huggingface_hub import HfApi
import os

api = HfApi()
api.upload_folder(
    folder_path='.',
    repo_id=f'{os.environ["HF_USERNAME"]}/{os.environ["HF_SPACE_NAME"]}',
    repo_type='space',
    token=os.environ["HF_TOKEN"],
    commit_message='Deploy Addis Suk Bot from GitHub Actions',
    ignore_patterns=[
        '.git/**',
        '__pycache__/**',
        '*.pyc',
        'data/**',
        'logs/**',
        '.env',
        '.env.local',
        '*.db',
        'readme',
        '.pytest_cache/**',
        '.ruff_cache/**',
        '.mypy_cache/**',
        '.vscode/**',
        '.idea/**',
    ]
)
print('✅ Successfully pushed to Hugging Face Spaces')
