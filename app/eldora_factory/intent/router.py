def route(prompt, task_type):
    if task_type == 'image':
        return 'sdxl'
    if task_type == 'video':
        return 'svd'
    if task_type == 'audio':
        return 'whisper'
    return 'sdxl'
