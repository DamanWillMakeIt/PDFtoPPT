import os
import cloudinary
import cloudinary.uploader

class CloudinaryService:
    @staticmethod
    def init_config():
        # Ensure config is loaded from environment variables
        cloudinary.config(
            cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
            api_key=os.getenv("CLOUDINARY_API_KEY"),
            api_secret=os.getenv("CLOUDINARY_API_SECRET"),
            secure=True
        )

    @staticmethod
    def upload_ppt(file_path: str, filename_without_ext: str) -> str:
        """
        Uploads a PPTX file to Cloudinary and returns the secure URL.
        """
        CloudinaryService.init_config()
        
        print(f"☁️ Uploading {filename_without_ext} to Cloudinary...")
        
        try:
            # resource_type="raw" is CRITICAL for non-image files (PPTX, PDF, DOCX)
            response = cloudinary.uploader.upload(
                file_path, 
                resource_type="raw", 
                public_id=f"presentations/{filename_without_ext}",
                overwrite=True
            )
            
            url = response['secure_url']
            print(f"✅ Upload Complete: {url}")
            return url
            
        except Exception as e:
            print(f"❌ Cloudinary Upload Error: {e}")
            raise e