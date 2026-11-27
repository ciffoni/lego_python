@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM ==================================================
REM   Uso via linha de comando (todos opcionais):
REM   setup_github.bat -r "nome-repo" -p -m "Primeiro commit" -u "Seu Nome" -e "seu@email.com" -s
REM ==================================================

set "REPO_NOME="
set "FLAG_VIS=--public"
set "VIS_DEFINIDA=0"
set "MSG_COMMIT="
set "GIT_USER="
set "GIT_EMAIL="
set "ESCOPO_GIT=--local"
set "SILENCIOSO=0"

:parse_args
if "%~1"=="" goto fim_args

if /i "%~1"=="-r" ( set "REPO_NOME=%~2" & shift & shift & goto parse_args )
if /i "%~1"=="-p" ( set "FLAG_VIS=--private" & set "VIS_DEFINIDA=1" & shift & goto parse_args )
if /i "%~1"=="-m" ( set "MSG_COMMIT=%~2" & shift & shift & goto parse_args )
if /i "%~1"=="-u" ( set "GIT_USER=%~2" & shift & shift & goto parse_args )
if /i "%~1"=="-e" ( set "GIT_EMAIL=%~2" & shift & shift & goto parse_args )
if /i "%~1"=="-g" ( set "ESCOPO_GIT=--global" & shift & goto parse_args )
if /i "%~1"=="-s" ( set "SILENCIOSO=1" & shift & goto parse_args )

echo [AVISO] Parametro desconhecido ignorado: %~1
shift
goto parse_args

:fim_args

echo ==================================================
echo   Automacao de Repositorio Git e GitHub
echo ==================================================
echo.

REM --------------------------------------------------
REM 1. Verificacao e instalacao automatica do Git
REM --------------------------------------------------
git --version >nul 2>&1
if errorlevel 1 (
    echo [INFO] Git nao encontrado. Tentando instalar via winget...
    winget --version >nul 2>&1
    if errorlevel 1 (
        echo [ERRO] Winget nao disponivel. Baixe o Git manualmente em: https://git-scm.com/download/win
        call :pausar
        exit /b 1
    )

    winget install --id Git.Git -e --source winget --accept-package-agreements --accept-source-agreements
    if errorlevel 1 (
        echo [ERRO] Falha ao instalar o Git. Tente executar o terminal como Administrador.
        call :pausar
        exit /b 1
    )

    REM Atualiza o PATH da sessao atual para reconhecer o Git imediatamente
    if exist "C:\Program Files\Git\cmd" set "PATH=%PATH%;C:\Program Files\Git\cmd"
    if exist "%LocalAppData%\Programs\Git\cmd" set "PATH=%PATH%;%LocalAppData%\Programs\Git\cmd"

    git --version >nul 2>&1
    if errorlevel 1 (
        echo [ERRO] Git instalado, mas o PATH precisa ser recarregado. Feche e abra o terminal novamente.
        call :pausar
        exit /b 1
    )
    echo [OK] Git instalado com sucesso!
)

REM --------------------------------------------------
REM 2. Verificacao e instalacao automatica do GitHub CLI
REM --------------------------------------------------
gh --version >nul 2>&1
if errorlevel 1 (
    echo [INFO] GitHub CLI ^(gh^) nao encontrado. Tentando instalar via winget...
    winget install --id GitHub.cli -e --source winget --accept-package-agreements --accept-source-agreements
    if errorlevel 1 (
        echo [ERRO] Falha ao instalar o GitHub CLI. Baixe em: https://cli.github.com/
        call :pausar
        exit /b 1
    )

    REM Atualiza o PATH da sessao atual para reconhecer o gh imediatamente
    if exist "C:\Program Files\GitHub CLI" set "PATH=%PATH%;C:\Program Files\GitHub CLI"
    if exist "%LocalAppData%\Programs\GitHub CLI" set "PATH=%PATH%;%LocalAppData%\Programs\GitHub CLI"

    gh --version >nul 2>&1
    if errorlevel 1 (
        echo [ERRO] GitHub CLI instalado. Feche e abra o terminal para atualizar o PATH.
        call :pausar
        exit /b 1
    )
    echo [OK] GitHub CLI instalado com sucesso!
)

REM --------------------------------------------------
REM 3. Autenticacao no GitHub CLI
REM --------------------------------------------------
gh auth status >nul 2>&1
if errorlevel 1 (
    if "%SILENCIOSO%"=="0" (
        echo [INFO] Voce ainda nao esta autenticado no GitHub. Iniciando login...
        gh auth login
        gh auth status >nul 2>&1
        if errorlevel 1 (
            echo [ERRO] Falha na autenticacao do GitHub.
            call :pausar
            exit /b 1
        )
    ) else (
        echo [ERRO] GitHub CLI nao autenticado e modo silencioso ativo. Execute: gh auth login
        exit /b 1
    )
)

REM --------------------------------------------------
REM 4. Inicializacao e configuracao de identidade Git
REM --------------------------------------------------
if not exist ".git" (
    git init -b main >nul
) else (
    git branch -M main >nul
)

for /f "delims=" %%U in ('git config user.name 2^>nul') do set "ATUAL_USER=%%U"
for /f "delims=" %%E in ('git config user.email 2^>nul') do set "ATUAL_EMAIL=%%E"

if not "%GIT_USER%"=="" (
    git config %ESCOPO_GIT% user.name "%GIT_USER%"
) else if "%ATUAL_USER%"=="" (
    if "%SILENCIOSO%"=="0" (
        set /p "GIT_USER=Git user.name nao definido. Informe seu nome: "
        if not "!GIT_USER!"=="" git config %ESCOPO_GIT% user.name "!GIT_USER!"
    ) else (
        echo [ERRO] user.name nao configurado. Use -u "Nome".
        exit /b 1
    )
)

if not "%GIT_EMAIL%"=="" (
    git config %ESCOPO_GIT% user.email "%GIT_EMAIL%"
) else if "%ATUAL_EMAIL%"=="" (
    if "%SILENCIOSO%"=="0" (
        set /p "GIT_EMAIL=Git user.email nao definido. Informe seu e-mail: "
        if not "!GIT_EMAIL!"=="" git config %ESCOPO_GIT% user.email "!GIT_EMAIL!"
    ) else (
        echo [ERRO] user.email nao configurado. Use -e "email".
        exit /b 1
    )
)

REM --------------------------------------------------
REM 5. Dados do repositorio e commit inicial
REM --------------------------------------------------
for %%I in ("%CD%") do set "PASTA_ATUAL=%%~nxI"

if "%REPO_NOME%"=="" (
    if "%SILENCIOSO%"=="0" (
        set /p "REPO_NOME=Nome do repositorio [%PASTA_ATUAL%]: "
    )
    if "!REPO_NOME!"=="" set "REPO_NOME=%PASTA_ATUAL%"
)

if "%VIS_DEFINIDA%"=="0" (
    if "%SILENCIOSO%"=="0" (
        set /p "VIS_INPUT=Tornar o repositorio privado? (S/N) [N]: "
        if /i "!VIS_INPUT!"=="S" set "FLAG_VIS=--private"
    )
)

if "%MSG_COMMIT%"=="" (
    if "%SILENCIOSO%"=="0" (
        set /p "MSG_COMMIT=Mensagem do commit inicial [Initial commit]: "
    )
    if "!MSG_COMMIT!"=="" set "MSG_COMMIT=Initial commit"
)

if not exist ".gitignore" (
    (
        echo *.log
        echo .DS_Store
        echo Thumbs.db
        echo node_modules/
        echo __pycache__/
        echo bin/
        echo obj/
        echo .env
    ) > .gitignore
)

echo [1/3] Adicionando arquivos e realizando commit...
git add .
git commit -m "%MSG_COMMIT%"
if errorlevel 1 (
    echo [AVISO] Nada novo para comitar ou commit ja existente.
)

echo [2/3] Criando repositorio "%REPO_NOME%" (%FLAG_VIS%) no GitHub...
gh repo create "%REPO_NOME%" %FLAG_VIS% --source=. --remote=origin
if errorlevel 1 (
    echo [ERRO] Falha ao criar o repositorio no GitHub.
    call :pausar
    exit /b 1
)

echo [3/3] Enviando codigo para origin/main...
git push -u origin main
if errorlevel 1 (
    echo [ERRO] Falha ao executar git push.
    call :pausar
    exit /b 1
)

echo.
echo [SUCESSO] Projeto publicado no GitHub!

if "%SILENCIOSO%"=="0" (
    gh repo view "%REPO_NOME%" --web >nul 2>&1
    pause
)

endlocal
exit /b 0

:pausar
if "%SILENCIOSO%"=="0" pause
exit /b 0