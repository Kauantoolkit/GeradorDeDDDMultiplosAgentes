# Script para adicionar Ollama ao PATH do Windows
# Execute este script como Administrador

$ollamaPath = "C:\Users\kauan\AppData\Local\Programs\ollama"

# Verifica se o diretório existe
if (Test-Path $ollamaPath) {
    # Obtém o PATH atual do usuário
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
    
    # Verifica se já está no PATH
    if ($currentPath -notlike "*$ollamaPath*") {
        # Adiciona ao PATH do usuário
        $newPath = "$currentPath;$ollamaPath"
        [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
        
        Write-Host "Ollama adicionado ao PATH com sucesso!" -ForegroundColor Green
        Write-Host "Novo PATH: $newPath"
        Write-Host ""
        Write-Host "IMPORTANTE: Feche e reabra o terminal (PowerShell/CMD) para生效"
    } else {
        Write-Host "Ollama já está no PATH!" -ForegroundColor Yellow
    }
} else {
    Write-Host "Diretório do Ollama não encontrado em: $ollamaPath" -ForegroundColor Red
    Write-Host "Verifique a instalação do Ollama"
}

# Para VSCode: também adicionar ao PATH da sessão atual
$env:Path += ";$ollamaPath"
Write-Host "PATH da sessão atual atualizado"

# Testa o comando
Write-Host ""
Write-Host "Testando comando ollama..."
& "$ollamaPath\ollama.exe" --version
