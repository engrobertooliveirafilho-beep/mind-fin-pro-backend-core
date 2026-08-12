from api.runpod_client import RunPodClient

client = RunPodClient('RUNPOD_ENDPOINT', 'API_KEY')

def run_image(prompt):
    return client.run({
        'type': 'image',
        'prompt': prompt
    })
