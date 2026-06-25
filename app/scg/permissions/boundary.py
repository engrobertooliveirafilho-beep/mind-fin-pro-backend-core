class PermissionBoundary:
    def validate(self, source):
        allowed = ["user_camera", "user_microphone", "user_text", "user_files"]
        return source in allowed
