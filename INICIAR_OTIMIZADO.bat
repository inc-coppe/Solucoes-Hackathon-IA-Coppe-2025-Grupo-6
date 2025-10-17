@echo off
echo ========================================
echo    Gestao Inteligente de Vagas - GIV - Versao Otimizada
echo ========================================
echo.
echo Iniciando servidor...
echo.
echo URL: http://127.0.0.1:8001
echo Usuario: admin
echo Senha: admin123
echo.
echo Pressione Ctrl+C para parar
echo ========================================
echo.

REM Verificar se Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    echo Instale Python 3.8+ e tente novamente.
    pause
    exit /b 1
)

REM Verificar se arquivo existe
if not exist "dashboard_otimizado.py" (
    echo ERRO: dashboard_otimizado.py nao encontrado!
    echo Certifique-se de estar no diretorio correto.
    pause
    exit /b 1
)

REM Verificar dependencias
if not exist "requirements_otimizado.txt" (
    echo AVISO: requirements_otimizado.txt nao encontrado
    echo Usando requirements.txt...
    if exist "requirements.txt" (
        pip install -r requirements.txt
    ) else (
        echo ERRO: Nenhum arquivo de dependencias encontrado!
        pause
        exit /b 1
    )
) else (
    echo Instalando dependencias otimizadas...
    pip install -r requirements_otimizado.txt
)

REM Iniciar dashboard
echo.
echo Iniciando GIV...
python dashboard_otimizado.py

pause

