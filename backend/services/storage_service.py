import boto3
import os
from botocore.exceptions import ClientError, NoCredentialsError
from werkzeug.datastructures import FileStorage
from PIL import Image
import io
import uuid
from typing import Optional, Tuple
import structlog

logger = structlog.get_logger()

class StorageService:
    """Service for handling file storage operations"""
    
    def __init__(self):
        self.use_s3 = all([
            os.getenv('AWS_ACCESS_KEY_ID'),
            os.getenv('AWS_SECRET_ACCESS_KEY'),
            os.getenv('AWS_S3_BUCKET')
        ])
        
        if self.use_s3:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('AWS_REGION', 'us-east-1')
            )
            self.bucket_name = os.getenv('AWS_S3_BUCKET')
            logger.info("StorageService initialized with S3", bucket=self.bucket_name)
        else:
            # Fallback to local storage
            self.local_storage_path = os.getenv('UPLOAD_FOLDER', 'uploads')
            os.makedirs(self.local_storage_path, exist_ok=True)
            os.makedirs(os.path.join(self.local_storage_path, 'originals'), exist_ok=True)
            os.makedirs(os.path.join(self.local_storage_path, 'results'), exist_ok=True)
            logger.info("StorageService initialized with local storage", 
                       path=self.local_storage_path)
    
    def upload_file(self, file: FileStorage, filename: str, folder: str = 'originals') -> str:
        """Upload file to storage and return URL"""
        try:
            if self.use_s3:
                return self._upload_to_s3(file, filename, folder)
            else:
                return self._upload_to_local(file, filename, folder)
        except Exception as e:
            logger.error("File upload failed", filename=filename, error=str(e))
            raise
    
    def upload_image(self, image: Image.Image, filename: str, folder: str = 'results') -> str:
        """Upload PIL Image to storage and return URL"""
        try:
            # Convert PIL Image to bytes
            img_bytes = io.BytesIO()
            
            # Determine format from filename extension
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext in ['.jpg', '.jpeg']:
                image.save(img_bytes, format='JPEG', quality=95, optimize=True)
                content_type = 'image/jpeg'
            elif file_ext == '.png':
                image.save(img_bytes, format='PNG', optimize=True)
                content_type = 'image/png'
            elif file_ext == '.webp':
                image.save(img_bytes, format='WebP', quality=95, optimize=True)
                content_type = 'image/webp'
            else:
                # Default to JPEG
                image.save(img_bytes, format='JPEG', quality=95, optimize=True)
                content_type = 'image/jpeg'
                filename = os.path.splitext(filename)[0] + '.jpg'
            
            img_bytes.seek(0)
            
            if self.use_s3:
                return self._upload_bytes_to_s3(img_bytes, filename, folder, content_type)
            else:
                return self._upload_bytes_to_local(img_bytes, filename, folder)
                
        except Exception as e:
            logger.error("Image upload failed", filename=filename, error=str(e))
            raise
    
    def _upload_to_s3(self, file: FileStorage, filename: str, folder: str) -> str:
        """Upload file to S3"""
        try:
            key = f"{folder}/{filename}"
            
            # Determine content type
            content_type = self._get_content_type(filename)
            
            self.s3_client.upload_fileobj(
                file,
                self.bucket_name,
                key,
                ExtraArgs={
                    'ContentType': content_type,
                    'CacheControl': 'max-age=31536000',  # 1 year cache
                    'ACL': 'public-read'
                }
            )
            
            url = f"https://{self.bucket_name}.s3.{os.getenv('AWS_REGION', 'us-east-1')}.amazonaws.com/{key}"
            logger.info("File uploaded to S3", filename=filename, url=url)
            return url
            
        except ClientError as e:
            logger.error("S3 upload failed", filename=filename, error=str(e))
            raise
        except NoCredentialsError:
            logger.error("AWS credentials not found")
            raise
    
    def _upload_bytes_to_s3(self, file_bytes: io.BytesIO, filename: str, folder: str, content_type: str) -> str:
        """Upload bytes to S3"""
        try:
            key = f"{folder}/{filename}"
            
            self.s3_client.upload_fileobj(
                file_bytes,
                self.bucket_name,
                key,
                ExtraArgs={
                    'ContentType': content_type,
                    'CacheControl': 'max-age=31536000',  # 1 year cache
                    'ACL': 'public-read'
                }
            )
            
            url = f"https://{self.bucket_name}.s3.{os.getenv('AWS_REGION', 'us-east-1')}.amazonaws.com/{key}"
            logger.info("Bytes uploaded to S3", filename=filename, url=url)
            return url
            
        except ClientError as e:
            logger.error("S3 bytes upload failed", filename=filename, error=str(e))
            raise
    
    def _upload_to_local(self, file: FileStorage, filename: str, folder: str) -> str:
        """Upload file to local storage"""
        try:
            folder_path = os.path.join(self.local_storage_path, folder)
            os.makedirs(folder_path, exist_ok=True)
            
            file_path = os.path.join(folder_path, filename)
            file.save(file_path)
            
            # Return relative URL for local storage
            url = f"/uploads/{folder}/{filename}"
            logger.info("File uploaded locally", filename=filename, path=file_path)
            return url
            
        except Exception as e:
            logger.error("Local upload failed", filename=filename, error=str(e))
            raise
    
    def _upload_bytes_to_local(self, file_bytes: io.BytesIO, filename: str, folder: str) -> str:
        """Upload bytes to local storage"""
        try:
            folder_path = os.path.join(self.local_storage_path, folder)
            os.makedirs(folder_path, exist_ok=True)
            
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'wb') as f:
                f.write(file_bytes.getvalue())
            
            # Return relative URL for local storage
            url = f"/uploads/{folder}/{filename}"
            logger.info("Bytes uploaded locally", filename=filename, path=file_path)
            return url
            
        except Exception as e:
            logger.error("Local bytes upload failed", filename=filename, error=str(e))
            raise
    
    def delete_file(self, file_url: str) -> bool:
        """Delete file from storage"""
        try:
            if self.use_s3 and file_url.startswith('https://'):
                return self._delete_from_s3(file_url)
            else:
                return self._delete_from_local(file_url)
        except Exception as e:
            logger.error("File deletion failed", url=file_url, error=str(e))
            return False
    
    def _delete_from_s3(self, file_url: str) -> bool:
        """Delete file from S3"""
        try:
            # Extract key from URL
            key = file_url.split(f"{self.bucket_name}.s3.{os.getenv('AWS_REGION', 'us-east-1')}.amazonaws.com/")[1]
            
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            logger.info("File deleted from S3", url=file_url)
            return True
            
        except ClientError as e:
            logger.error("S3 deletion failed", url=file_url, error=str(e))
            return False
    
    def _delete_from_local(self, file_url: str) -> bool:
        """Delete file from local storage"""
        try:
            # Convert URL to local file path
            if file_url.startswith('/uploads/'):
                relative_path = file_url[9:]  # Remove '/uploads/' prefix
                file_path = os.path.join(self.local_storage_path, relative_path)
                
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info("File deleted locally", path=file_path)
                    return True
                else:
                    logger.warning("File not found for deletion", path=file_path)
                    return False
            else:
                logger.error("Invalid local file URL", url=file_url)
                return False
                
        except Exception as e:
            logger.error("Local deletion failed", url=file_url, error=str(e))
            return False
    
    def get_file_info(self, file_url: str) -> Optional[dict]:
        """Get file information"""
        try:
            if self.use_s3 and file_url.startswith('https://'):
                return self._get_s3_file_info(file_url)
            else:
                return self._get_local_file_info(file_url)
        except Exception as e:
            logger.error("Get file info failed", url=file_url, error=str(e))
            return None
    
    def _get_s3_file_info(self, file_url: str) -> Optional[dict]:
        """Get S3 file information"""
        try:
            key = file_url.split(f"{self.bucket_name}.s3.{os.getenv('AWS_REGION', 'us-east-1')}.amazonaws.com/")[1]
            
            response = self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
            
            return {
                'size': response['ContentLength'],
                'last_modified': response['LastModified'],
                'content_type': response['ContentType'],
                'etag': response['ETag']
            }
            
        except ClientError as e:
            logger.error("S3 file info failed", url=file_url, error=str(e))
            return None
    
    def _get_local_file_info(self, file_url: str) -> Optional[dict]:
        """Get local file information"""
        try:
            if file_url.startswith('/uploads/'):
                relative_path = file_url[9:]
                file_path = os.path.join(self.local_storage_path, relative_path)
                
                if os.path.exists(file_path):
                    stat = os.stat(file_path)
                    return {
                        'size': stat.st_size,
                        'last_modified': stat.st_mtime,
                        'content_type': self._get_content_type(file_path)
                    }
                else:
                    return None
            else:
                return None
                
        except Exception as e:
            logger.error("Local file info failed", url=file_url, error=str(e))
            return None
    
    def _get_content_type(self, filename: str) -> str:
        """Get content type based on file extension"""
        ext = os.path.splitext(filename)[1].lower()
        content_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.webp': 'image/webp',
            '.gif': 'image/gif'
        }
        return content_types.get(ext, 'application/octet-stream')
    
    def generate_presigned_url(self, file_url: str, expiration: int = 3600) -> Optional[str]:
        """Generate presigned URL for S3 files"""
        if not self.use_s3 or not file_url.startswith('https://'):
            return file_url  # Return original URL for local files
        
        try:
            key = file_url.split(f"{self.bucket_name}.s3.{os.getenv('AWS_REGION', 'us-east-1')}.amazonaws.com/")[1]
            
            presigned_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': key},
                ExpiresIn=expiration
            )
            
            return presigned_url
            
        except ClientError as e:
            logger.error("Presigned URL generation failed", url=file_url, error=str(e))
            return None

# Global service instance
storage_service = StorageService()
