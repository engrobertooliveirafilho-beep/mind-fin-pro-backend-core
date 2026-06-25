Write-Host 'Installing GPU stack...'

# Python AI stack
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install diffusers transformers accelerate
pip install opencv-python ffmpeg-python
pip install fastapi uvicorn
pip install redis supabase

Write-Host 'Core AI dependencies installed'
