from abc import ABC, abstractmethod

import io


class S3Interface(ABC):
    @abstractmethod
    def upload_file(self, file_path: str, object_name: str) -> None:
        pass

    @abstractmethod
    def put_object(
        self,
        object_name: str,
        data: io.BytesIO,
        size: int,
        content_type: str = "application/octet-stream",
    ) -> None:
        pass

    @abstractmethod
    def download_file(self, object_name: str, file_path: str) -> None:
        pass

    @abstractmethod
    def delete_file(self, object_name: str) -> None:
        pass

    @abstractmethod
    def generate_presigned_url(self, object_name: str, expiration: int = 3600) -> str:
        pass
