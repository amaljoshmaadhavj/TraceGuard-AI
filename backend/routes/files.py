"""
File upload and management routes
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import Optional
import os
import shutil
from datetime import datetime
import uuid
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# In-memory storage for demo (replace with database later)
uploaded_files = {}


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    category: Optional[str] = Form(None),
    analysis_type: Optional[str] = Form(None),
    notes: Optional[str] = Form(None)
):
    """
    Upload an EVTX or PCAP file
    Optional parameters:
    - category: The forensic category (execution, credential_access, etc.)
    - analysis_type: Type of analysis (General Analysis, Image Analysis, etc.)
    - notes: Additional context about the file
    """
    try:
        # Validate file type
        allowed_extensions = ['.evtx', '.pcap']
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        # Handle files with no extension that are clearly network logs
        if file_ext == '' and ('ucap' in file.filename.lower() or 'pcap' in file.filename.lower()):
            file_ext = '.pcap'
        
        if file_ext not in allowed_extensions:
            raise HTTPException(status_code=400, detail=f"File type '{file_ext}' not supported. Supported: .evtx, .pcap")
        
        # Use provided category or default to unknown
        target_category = category or "execution"
        
        # Override category based on extension if it's a network log
        if file_ext == '.pcap':
            target_category = "network_logs"
        
        # Create file ID
        file_id = str(uuid.uuid4())
        
        # Save file to the correct category folder
        data_dir = f"../data/{target_category}"
        os.makedirs(data_dir, exist_ok=True)
        
        file_path = os.path.join(data_dir, file.filename)
        
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Store file info
        file_info = {
            'id': file_id,
            'filename': file.filename,
            'category': target_category,
            'file_type': file_ext,
            'size': len(content),
            'upload_date': datetime.now().isoformat(),
            'status': 'ready',
            'path': file_path,
            'analysis_type': analysis_type or 'General Analysis',
            'notes': notes or ''
        }
        
        uploaded_files[file_id] = file_info
        
        logger.info(f"File uploaded to {target_category}: {file.filename}")
        
        return {
            "success": True,
            "message": f"File {file.filename} uploaded successfully to {target_category}",
            "file_id": file_id,
            "filename": file.filename,
            "category": target_category,
            "analysis_type": analysis_type or "General Analysis"
        }
    
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def list_files():
    """
    Get list of uploaded files
    """
    try:
        files_list = []
        
        # Get files from data directory
        base_data_dir = "../data"
        if os.path.exists(base_data_dir):
            for category in os.listdir(base_data_dir):
                category_path = os.path.join(base_data_dir, category)
                if os.path.isdir(category_path):
                    for filename in os.listdir(category_path):
                        filepath = os.path.join(category_path, filename)
                        if os.path.isfile(filepath):
                            file_size = os.path.getsize(filepath)
                            files_list.append({
                                'id': filename,
                                'filename': filename,
                                'category': category,
                                'type': os.path.splitext(filename)[1].lower(),
                                'size': file_size,
                                'upload_date': datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat(),
                                'status': 'indexed'
                            })
        
        return {
            "total": len(files_list),
            "files": files_list
        }
    
    except Exception as e:
        logger.error(f"List files error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{file_id}")
async def delete_file(file_id: str):
    """
    Delete a file
    """
    try:
        if file_id in uploaded_files:
            file_info = uploaded_files[file_id]
            # Delete physical file
            if os.path.exists(file_info['path']):
                os.remove(file_info['path'])
            del uploaded_files[file_id]
        
        logger.info(f"File deleted: {file_id}")
        
        return {"success": True, "message": "File deleted successfully"}
    
    except Exception as e:
        logger.error(f"Delete file error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
