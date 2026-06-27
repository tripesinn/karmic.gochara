import sys
from huggingface_hub import hf_hub_download

repo_id = "litert-community/gemma-4-E2B-it-litert-lm"
filename = "gemma-4-E2B-it-web.task"
local_dir = "scratch"
token = "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"

print(f"Starting authenticated download of {filename} from {repo_id}...")
try:
    path = hf_hub_download(
        repo_id=repo_id,
        filename=filename,
        local_dir=local_dir,
        token=token
    )
    print(f"Download successful! Saved to: {path}")
except Exception as e:
    print(f"Error during download: {e}")
    sys.exit(1)
