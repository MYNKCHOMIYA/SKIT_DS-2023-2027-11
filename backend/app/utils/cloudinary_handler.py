import cloudinary
import cloudinary.uploader
from app.core.config import settings

# Initialize the connection to your Cloudinary account
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,
)


def upload_image(file_obj, folder_name: str = "gfpms/profiles"):
    """
    Uploads an image to Cloudinary and returns the secure URL.
    """
    try:
        # We pass the raw file byte stream directly to Cloudinary
        response = cloudinary.uploader.upload(
            file_obj, folder=folder_name, resource_type="image"
        )
        return response.get("secure_url")
    except Exception as e:
        print(f"Cloudinary upload failed: {e}")
        return None
