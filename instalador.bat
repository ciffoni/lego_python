@echo off
chcp 65001 > nul
title Instalador Completo: Pybricks, LEGO EV3, VS Code e API Flask
color 0A

echo ============================================================================
echo    CONFIGURACAO COMPLETA: PYBRICKS + EV3 (VS CODE) + API FLASK / MYSQL
echo ============================================================================
echo.

:: 1. Verificar ou instalar Python
echo [1/5] Verificando instalacao do Python...
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Python nao encontrado. Tentando instalar via winget...
    winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
    if %errorlevel% neq 0 (
        echo [ERRO] Nao foi possivel instalar automaticamente.
        echo Instale o Python manualmente marcando "Add Python to PATH".
        start https://www.python.org/downloads/
        pause
        exit /b
    )
    echo [AVISO] Python instalado! Feche e execute este script novamente para atualizar o PATH.
    pause
    exit /b
)
python --version
echo.

:: 2. Atualizar o pip
echo [2/5] Atualizando o gerenciador de pacotes (pip)...
python -m pip install --upgrade pip --user
echo.

:: 3. Instalar pacotes Pybricks, ev3dev2 e bibliotecas da API (Flask + MySQL)
echo [3/5] Instalando pacotes Python (Pybricks, ev3dev2, Flask e MySQL)...
python -m pip install pybricks pybricksdev python-ev3dev2 flask mysql-connector-python --user
echo.

:: 4. Verificar ou instalar o VS Code
echo [4/5] Verificando instalacao do Visual Studio Code...
where code > nul 2>&1
if %errorlevel% neq 0 (
    echo VS Code nao encontrado. Tentando instalar via winget...
    winget install -e --id Microsoft.VisualStudioCode --accept-package-agreements --accept-source-agreements
)

:: 5. Instalar extensoes do VS Code (Python + LEGO MINDSTORMS EV3 MicroPython)
echo [5/5] Instalando extensoes no VS Code...
where code > nul 2>&1
if %errorlevel% equ 0 (
    echo Instalando extensao oficial do Python...
    call code --install-extension ms-python.python
    echo Instalando extensao LEGO MINDSTORMS EV3 MicroPython...
    call code --install-extension lego-education.ev3-micropython
) else (
    echo [AVISO] VS Code ainda nao esta no PATH. Reinicie o terminal ou o PC e instale as extensoes:
    echo   - ms-python.python
    echo   - lego-education.ev3-micropython
)

echo.
echo ============================================================================
echo          RESUMO DO AMBIENTE CONFIGURADO E COMANDOS UTEIS
echo ============================================================================
echo.
echo * BIBLIOTECAS INSTALADAS:
echo   - pybricks / pybricksdev (Firmware e CLI Pybricks)
echo   - python-ev3dev2 (Autocomplete para scripts EV3Dev)
echo   - flask / mysql-connector-python (Servidor API e Banco de Dados)
echo.
echo * EXTENSOES DO VS CODE:
echo   - Python (Microsoft)
echo   - LEGO MINDSTORMS EV3 MicroPython (LEGO Education)
echo.
echo * COMANDOS UTEIS:
echo   - Rodar script Pybricks via Bluetooth/USB:
echo       pybricksdev run ble seu_script.py
echo       pybricksdev run usb seu_script.py
echo   - Iniciar sua API Flask:
echo       python api_get.py
echo.
echo ============================================================================
echo Configuracao concluida com sucesso!
echo ============================================================================
pause