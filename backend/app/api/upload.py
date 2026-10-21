from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
import cloudinary.uploader
from app.api.deps import get_current_active_user
from app.models.user import User

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
def upload_file(
    file: UploadFile = File(...), current_user: User = Depends(get_current_active_user)
):
    """
    Accepts a file (PDF, JPG, PNG) and uploads it to Cloudinary.
    Returns the secure URL to be stored in the database.
    """
    # 1. Validate file type (Optional but highly recommended for security)
    allowed_content_types = ["application/pdf", "image/jpeg", "image/png"]
    if file.content_type not in allowed_content_types:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only PDFs, JPEGs, and PNGs are allowed.",
        )

    try:
        # 2. Upload to a specific folder in Cloudinary to keep things organized
        upload_result = cloudinary.uploader.upload(
            file.file,
            folder="faculty_portfolio_assets",
            resource_type="auto",  # 'auto' allows both images and raw files like PDFs
        )

        # 3. Return the generated URL
        return {
            "filename": file.filename,
            "url": upload_result.get("secure_url"),
            "format": upload_result.get("format"),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"There was an error uploading the file: {str(e)}"
        )
