@echo off
echo ========================================
echo   API REST - Gestao Inteligente de Vagas
echo ========================================
echo.
echo Iniciando a API REST GIV...
echo.

REM Verificar se Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    echo Por favor, instale o Python 3.8 ou superior.
    pause
    exit /b 1
)

REM Verificar se as dependencias estao instaladas
echo Verificando dependencias...
python -c "import fastapi, polars, sklearn" >nul 2>&1
if errorlevel 1 (
    echo Instalando dependencias...
    pip install -r requirements_api_giv.txt
    if errorlevel 1 (
        echo ERRO: Falha ao instalar dependencias!
        pause
        exit /b 1
    )
)

REM Verificar se os dados estao disponiveis
if not exist "db\solicitacao-000000000000.parquet" (
    echo AVISO: Arquivos de dados nao encontrados na pasta db\
    echo A API pode nao funcionar corretamente sem os dados.
    echo.
)

echo.
echo ========================================
echo   INICIANDO SERVIDOR API
echo ========================================
echo.
echo URL Base: http://127.0.0.1:8000
echo Documentacao: http://127.0.0.1:8000/docs
echo ReDoc: http://127.0.0.1:8000/redoc
echo.
echo Pressione Ctrl+C para parar o servidor
echo.

REM Iniciar a API
python api_giv_completa.py

echo.
echo Servidor parado.
pause

