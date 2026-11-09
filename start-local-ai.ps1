# Quit an existing Ollama tray instance before using this server configuration.
$env:OLLAMA_NO_CLOUD = '1'
$env:OLLAMA_HOST = '127.0.0.1:11434'
$env:OLLAMA_NUM_PARALLEL = '1'
$env:OLLAMA_MAX_LOADED_MODELS = '1'
$env:OLLAMA_CONTEXT_LENGTH = '8192'
Write-Host 'Starting local Ollama. Leave this terminal open; Ctrl+C stops this server.'
ollama serve
