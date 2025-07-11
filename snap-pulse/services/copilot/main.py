import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from github import Github
import yaml
import tempfile
import logging
from typing import Dict, Any
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="SnapPulse Copilot", version="1.0.0")

# Use a lighter model for better performance
MODEL_NAME = "microsoft/DialoGPT-small"  # Smaller than medium, faster startup

# Configure 4-bit quantization for efficiency
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)
    bnb_4bit_use_double_quant=True,
)

# Load model and tokenizer (using a smaller model for demo)
MODEL_NAME = "microsoft/DialoGPT-medium"  # Using a smaller model for demo purposes
tokenizer = None
model = None

def load_model():
    global tokenizer, model
    try:
        logger.info("Loading model and tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        tokenizer.pad_token = tokenizer.eos_token
        
        # For demo purposes, we'll use CPU inference
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            torch_dtype=torch.float16,
            device_map="auto" if torch.cuda.is_available() else None,
        )
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        # For demo, we'll continue without the model

# Load model on startup
load_model()

class SnapcraftAnalysisRequest(BaseModel):
    snapcraft_yaml: str
    repository_url: str
    issue_number: int

class SnapcraftSuggestion(BaseModel):
    title: str
    description: str
    yaml_patch: str
    reasoning: str

PROMPT_TEMPLATE = """You are SnapCraftCopilot, an expert in Snapcraft package optimization.

The maintainer's snapcraft.yaml is below:

{snapcraft_yaml}

Analyze this snapcraft.yaml and suggest exactly three changes that will:
1. Reduce package size
2. Tighten confinement 
3. Improve security or performance

Return your response as valid YAML patches only. Focus on:
- Removing unnecessary dependencies
- Using more restrictive plugs
- Optimizing build configuration
- Using staged packages efficiently

Respond with actionable YAML changes."""

def generate_suggestions(snapcraft_yaml: str) -> list[SnapcraftSuggestion]:
    """Generate optimization suggestions for a snapcraft.yaml file."""
    
    # For demo purposes, return mock suggestions
    # In production, this would use the actual model
    suggestions = [
        SnapcraftSuggestion(
            title="Optimize build dependencies",
            description="Remove unnecessary build packages to reduce snap size",
            yaml_patch="""--- a/snapcraft.yaml
+++ b/snapcraft.yaml
@@ -10,7 +10,6 @@
   build-packages:
     - gcc
     - make
-    - python3-dev
     - pkg-config""",
            reasoning="python3-dev is often included in the base and doesn't need to be explicitly listed"
        ),
        SnapcraftSuggestion(
            title="Tighten confinement with specific plugs",
            description="Replace broad plugs with more specific ones",
            yaml_patch="""--- a/snapcraft.yaml
+++ b/snapcraft.yaml
@@ -5,7 +5,8 @@
 confinement: strict
 
 plugs:
-  - home
+  - home-read-only
+  - personal-files
   - network""",
            reasoning="Using home-read-only instead of home provides better security while maintaining functionality"
        ),
        SnapcraftSuggestion(
            title="Use stage-packages optimization",
            description="Minimize runtime dependencies",
            yaml_patch="""--- a/snapcraft.yaml
+++ b/snapcraft.yaml
@@ -15,8 +15,7 @@
   stage-packages:
     - libssl3
     - libcurl4
-    - ca-certificates
-    - curl""",
            reasoning="ca-certificates and curl are often available in the base, reducing snap size"
        )
    ]
    
    return suggestions

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model_loaded": model is not None}

@app.post("/analyze")
async def analyze_snapcraft(request: SnapcraftAnalysisRequest) -> dict:
    """Analyze a snapcraft.yaml and generate optimization suggestions."""
    try:
        # Get GitHub token
        github_token = os.environ.get("GITHUB_TOKEN")
        if not github_token:
            raise HTTPException(status_code=400, detail="GitHub token not configured")
        
        # Initialize GitHub client
        g = Github(github_token)
        
        # Parse repository URL to get owner/repo
        repo_parts = request.repository_url.replace("https://github.com/", "").split("/")
        if len(repo_parts) < 2:
            raise HTTPException(status_code=400, detail="Invalid repository URL")
        
        owner, repo_name = repo_parts[0], repo_parts[1]
        repo = g.get_repo(f"{owner}/{repo_name}")
        
        # Fetch current snapcraft.yaml
        try:
            snapcraft_file = repo.get_contents("snapcraft.yaml")
            current_yaml = snapcraft_file.decoded_content.decode('utf-8')
        except:
            try:
                snapcraft_file = repo.get_contents("snap/snapcraft.yaml")
                current_yaml = snapcraft_file.decoded_content.decode('utf-8')
            except:
                raise HTTPException(status_code=404, detail="snapcraft.yaml not found in repository")
        
        # Generate suggestions
        suggestions = generate_suggestions(current_yaml)
        
        # Create a branch and PR with improvements
        main_branch = repo.get_branch("main")
        new_branch_name = f"snappulse-optimization-{request.issue_number}"
        
        try:
            # Create new branch
            repo.create_git_ref(
                ref=f"refs/heads/{new_branch_name}",
                sha=main_branch.commit.sha
            )
            
            # Apply the first suggestion as an example
            if suggestions:
                improved_yaml = apply_yaml_patch(current_yaml, suggestions[0].yaml_patch)
                
                # Update the file
                repo.update_file(
                    path=snapcraft_file.path,
                    message=f"SnapPulse optimization: {suggestions[0].title}",
                    content=improved_yaml,
                    sha=snapcraft_file.sha,
                    branch=new_branch_name
                )
                
                # Create PR
                pr = repo.create_pull(
                    title=f"🚀 SnapPulse optimization suggestions (Issue #{request.issue_number})",
                    body=f"""## SnapPulse Optimization Report

This PR contains optimization suggestions for your snapcraft.yaml:

### {suggestions[0].title}
{suggestions[0].description}

**Reasoning:** {suggestions[0].reasoning}

### Additional Suggestions:
""" + "\n".join([f"- **{s.title}**: {s.description}" for s in suggestions[1:]]),
                    head=new_branch_name,
                    base="main"
                )
                
                return {
                    "status": "success",
                    "pr_url": pr.html_url,
                    "suggestions": [s.dict() for s in suggestions],
                    "repository_url": request.repository_url,
                    "analysis_timestamp": "2025-07-11T00:00:00Z"
                }
        except Exception as git_error:
            logger.error(f"Git operations failed: {git_error}")
            # Fallback to just returning suggestions
            pass
        
        return {
            "suggestions": [s.dict() for s in suggestions],
            "repository_url": request.repository_url,
            "analysis_timestamp": "2025-07-11T00:00:00Z"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

def apply_yaml_patch(original_yaml: str, patch: str) -> str:
    """Apply a YAML patch to the original content."""
    try:
        # Simple patch application - in production use ruamel.yaml
        lines = original_yaml.split('\n')
        patch_lines = patch.split('\n')
        
        # For demo, just append the patch
        return original_yaml + '\n\n# SnapPulse optimization:\n' + patch
    except Exception as e:
        logger.error(f"Failed to apply patch: {e}")
        return original_yaml

@app.post("/github-webhook")
async def handle_github_webhook(payload: dict):
    """Handle GitHub webhook for /snappulse fix commands."""
    try:
        # Check if this is an issue comment with /snappulse fix
        if (payload.get("action") == "created" and 
            "comment" in payload and 
            "/snappulse fix" in payload["comment"]["body"]):
            
            repo_url = payload["repository"]["html_url"]
            issue_number = payload["issue"]["number"]
            
            # For demo purposes, return success
            # In production, this would:
            # 1. Clone the repository
            # 2. Find snapcraft.yaml
            # 3. Generate suggestions
            # 4. Create a PR with improvements
            
            logger.info(f"Processing /snappulse fix request for {repo_url}#{issue_number}")
            
            return {
                "status": "processing",
                "message": f"Creating optimization PR for issue #{issue_number}",
                "repository": repo_url
            }
            
        return {"status": "ignored", "reason": "Not a /snappulse fix command"}
        
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Webhook processing failed: {str(e)}")

@app.get("/")
async def root():
    return {
        "message": "SnapPulse Copilot",
        "version": "1.0.0",
        "model": MODEL_NAME,
        "model_loaded": model is not None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
