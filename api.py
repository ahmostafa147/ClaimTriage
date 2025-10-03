"""FastAPI backend for Claims Triage Pro React frontend."""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import json
import os
from pathlib import Path
from typing import List, Dict, Any
import base64
from datetime import datetime

from pathway_pipe import get_pipeline, reset_pipeline
from counterfactual import CounterfactualAnalyzer
from fast_backtest import FastBacktester
from schema import StructuredClaim, RoutingDecision

app = FastAPI(title="Claims Triage Pro API", version="1.0.0")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize pipeline with Pathway and LandingAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set LandingAI API key
os.environ["LANDINGAI_API_KEY"] = "am43cmYzaGF3M2hhOXhiMWQ0a3B4OkZPcENsWE81WU9zUkdldU5pU0NDdDZGUm14MXE2MUFh"

# Initialize pipeline with REAL API - NO MOCK MODE
pipeline = get_pipeline("REAL", use_pathway=False)  # REAL API only
# Remove automatic processing - users must upload files

@app.get("/")
async def root():
    """Serve the React frontend."""
    return FileResponse("index.html")

@app.get("/api/metrics")
async def get_metrics():
    """Get current metrics."""
    metrics = pipeline.get_metrics()
    return {
        "extraction": metrics["extraction"],
        "routing": metrics["routing"],
        "total_claims": metrics.get("total_claims", len(pipeline.get_claims())),
        "route_distribution": metrics.get("route_distribution", {}),
        "queues": metrics["queues"]
    }

@app.get("/api/claims")
async def get_claims():
    """Get all claims."""
    claims = pipeline.get_claims()
    return [
        {
            "id": claim.file_id,
            "filename": claim.filename,
            "claimant_name": claim.claimant_name,
            "policy_id": claim.policy_id,
            "incident_date": claim.incident_date,
            "claim_amount_total_usd": claim.claim_amount_total_usd,
            "injury_severity": claim.injury_severity,
            "incident_type": claim.incident_type,
            "repeat_claims_count": claim.repeat_claims_count,
            "adverse_keywords": claim.adverse_keywords,
            "confidences": claim.confidences
        }
        for claim in claims
    ]

@app.get("/api/claims/{claim_id}")
async def get_claim(claim_id: str):
    """Get specific claim by ID."""
    claim = pipeline.get_claim_by_id(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    return {
        "id": claim.file_id,
        "filename": claim.filename,
        "claimant_name": claim.claimant_name,
        "policy_id": claim.policy_id,
        "incident_date": claim.incident_date,
        "claim_amount_total_usd": claim.claim_amount_total_usd,
        "injury_severity": claim.injury_severity,
        "incident_type": claim.incident_type,
        "repeat_claims_count": claim.repeat_claims_count,
        "adverse_keywords": claim.adverse_keywords,
        "confidences": claim.confidences
    }

@app.get("/api/decisions/{claim_id}")
async def get_decision(claim_id: str):
    """Get routing decision for specific claim."""
    decision = pipeline.get_decision_by_id(claim_id)
    if not decision:
        # Debug: check if claim exists
        claim = pipeline.get_claim_by_id(claim_id)
        if claim:
            raise HTTPException(status_code=404, detail=f"Decision not found for claim {claim_id} (claim exists but no decision)")
        else:
            raise HTTPException(status_code=404, detail=f"Claim {claim_id} not found")
    
    return {
        "route": decision.route,
        "rule_fired": decision.rule_fired,
        "rationale": decision.rationale,
        "evidence_pointers": decision.evidence_pointers,
        "safety_flags": getattr(decision, 'safety_flags', []),
        "low_confidence_fields": getattr(decision, 'low_confidence_fields', []),
        "sha256_raw": getattr(decision, 'sha256_raw', ''),
        "sha256_structured": getattr(decision, 'sha256_structured', ''),
        "created_at": getattr(decision, 'created_at', ''),
        "decision_id": decision.decision_id
    }

@app.get("/api/pdf/{filename}")
async def get_pdf(filename: str):
    """Get PDF file."""
    possible_paths = [
        Path("demo_data/inbox") / filename,
        Path("demo_data/mock_docs") / filename
    ]
    
    for path in possible_paths:
        if path.exists():
            return FileResponse(path, media_type="application/pdf")
    
    raise HTTPException(status_code=404, detail="PDF not found")

@app.get("/api/pdf/{filename}/preview")
async def get_pdf_preview(filename: str):
    """Get PDF preview as base64."""
    possible_paths = [
        Path("demo_data/inbox") / filename,
        Path("demo_data/mock_docs") / filename
    ]
    
    for path in possible_paths:
        if path.exists():
            try:
                # Convert PDF to base64 for preview
                with open(path, "rb") as f:
                    pdf_bytes = f.read()
                    pdf_base64 = base64.b64encode(pdf_bytes).decode()
                    return {"preview": f"data:application/pdf;base64,{pdf_base64}"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error reading PDF: {str(e)}")
    
    raise HTTPException(status_code=404, detail="PDF not found")

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload and process a PDF file."""
    try:
        if not file.filename or not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Ensure inbox directory exists
        inbox_dir = Path("demo_data/inbox")
        inbox_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename to avoid conflicts
        import uuid
        unique_filename = f"{uuid.uuid4().hex[:8]}_{file.filename}"
        inbox_path = inbox_dir / unique_filename
        
        # Save file to inbox
        with open(inbox_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        print(f"Saved file to: {inbox_path}")
        
        # Process file
        result = pipeline.process_file(inbox_path)
        if result:
            claim, decision = result
            return {
                "success": True,
                "message": f"Processed: {file.filename}",
                "claim_id": claim.file_id,
                "route": decision.route
            }
        else:
            # Try to get more specific error info
            if not inbox_path.exists():
                raise HTTPException(status_code=500, detail="File was not saved properly")
            
            # Check if file was already processed
            from storage import sha256_file
            file_hash = sha256_file(inbox_path)
            if file_hash in pipeline.processed_files:
                # Instead of failing, return the existing result
                existing_claims = pipeline.get_claims()
                for claim in existing_claims:
                    existing_decision = pipeline.get_decision_by_id(claim.file_id)
                    if existing_decision:
                        return {
                            "success": True,
                            "message": f"File already processed: {file.filename}",
                            "claim_id": claim.file_id,
                            "route": existing_decision.route
                        }
            
            raise HTTPException(status_code=500, detail="Failed to process file - extraction or routing failed")
            
    except Exception as e:
        print(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/api/generate-mock")
async def generate_mock():
    """Generate mock documents."""
    try:
        from ade_client import MockExtractor
        extractor = MockExtractor()
        files = extractor.generate_synthetic_claims()
        
        # Copy some to inbox for processing
        inbox_path = Path("demo_data/inbox")
        inbox_path.mkdir(parents=True, exist_ok=True)
        
        processed_count = 0
        for src_file in files[:6]:
            dest_file = inbox_path / src_file.name
            if not dest_file.exists():
                import shutil
                shutil.copy(src_file, dest_file)
                processed_count += 1
        
        # Process inbox
        results = pipeline.process_inbox()
        
        return {
            "success": True,
            "message": f"Generated {len(files)} mock documents, processed {len(results)} files"
        }
    except Exception as e:
        print(f"Generate mock error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate mock documents: {str(e)}")

@app.post("/api/process-inbox")
async def process_inbox():
    """Process all files in inbox."""
    results = pipeline.process_inbox()
    return {
        "success": True,
        "message": f"Processed {len(results)} files",
        "processed_count": len(results)
    }

@app.post("/api/rules")
async def update_rules(rules_data: Dict[str, str]):
    """Update routing rules."""
    try:
        # Handle both 'content' and 'rules' keys for compatibility
        rules_content = rules_data.get("content", "") or rules_data.get("rules", "")
        
        if not rules_content.strip():
            raise HTTPException(status_code=400, detail="Rules content cannot be empty")
        
        # Save rules
        with open("rules.yaml", "w") as f:
            f.write(rules_content)
        
        # Reload rules
        pipeline.reload_rules()
        
        # Run counterfactual analysis
        recent_claims = pipeline.get_recent_claims(10)
        if recent_claims:
            analyzer = CounterfactualAnalyzer()
            result = analyzer.analyze(recent_claims, rules_content)
            return {
                "success": True,
                "message": "Rules updated successfully",
                "counterfactual": result
            }
        
        return {
            "success": True,
            "message": "Rules updated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update rules: {str(e)}")

@app.get("/api/rules")
async def get_rules():
    """Get current rules."""
    rules_path = Path("rules.yaml")
    if rules_path.exists():
        with open(rules_path) as f:
            return {"content": f.read()}
    return {"content": ""}

@app.post("/api/backtest")
async def run_backtest():
    """Run backtest against gold labels."""
    backtester = FastBacktester()
    claims = pipeline.get_claims()
    decisions = pipeline.get_decisions()
    
    results = backtester.run_backtest(claims, decisions)
    
    return {
        "success": True,
        "results": results
    }

@app.get("/api/alternative-routes/{claim_id}")
async def get_alternative_routes(claim_id: str):
    """Get alternative routes for a claim."""
    claim = pipeline.get_claim_by_id(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    alternatives = pipeline.rule_engine.get_alternative_routes(claim)
    return {"alternatives": alternatives}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
