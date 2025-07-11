import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from github import Github
import yaml
import tempfile
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="SnapPulse Copilot", version="1.0.0")

# Configure 4-bit quantization
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
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
        suggestions = generate_suggestions(request.snapcraft_yaml)
        
        return {
            "suggestions": [s.dict() for s in suggestions],
            "repository_url": request.repository_url,
            "analysis_timestamp": "2025-07-11T00:00:00Z"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

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
