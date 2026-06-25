from supabase import create_client

class SupabaseStorage:
    def __init__(self, url, key):
        self.client = create_client(url, key)

    def upload(self, bucket, file_path):
        return self.client.storage.from_(bucket).upload(file_path, file_path)
