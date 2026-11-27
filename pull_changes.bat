@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ==================================================
echo   Atualizando Repositorio Local (Git Pull)
echo ==================================================
echo.

REM 1. Verifica se o Git esta disponivel
git --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Git nao encontrado no PATH.
    pause
    exit /b 1
)

REM 2. Verifica se a pasta atual e um repositorio Git
if not exist ".git" (
    echo [ERRO] Esta pasta nao possui um repositorio Git inicializado.
    pause
    exit /b 1
)

REM 3. Verifica se existe um remote "origin" configurado
git remote get-url origin >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Nenhum repositorio remoto ^(origin^) vinculado a esta pasta.
    pause
    exit /b 1
)

REM 4. Identifica a branch atual automaticamente (ex: main ou master)
for /f "delims=" %%B in ('git branch --show-current 2^>nul') do set "BRANCH_ATUAL=%%B"
if "%BRANCH_ATUAL%"=="" set "BRANCH_ATUAL=main"

REM 5. Verifica se existem modificacoes locais nao comitadas
set "TEM_ALTERACOES=0"
for /f "delims=" %%S in ('git status --porcelain') do set "TEM_ALTERACOES=1"

if "%TEM_ALTERACOES%"=="1" (
    echo [AVISO] Voce possui alteracoes locais nao salvas ^(commit^).
    set /p "USAR_STASH=Deseja guardar temporariamente ^(git stash^) antes de baixar e restaurar depois? (S/N) [S]: "
    if "!USAR_STASH!"=="" set "USAR_STASH=S"

    if /i "!USAR_STASH!"=="S" (
        echo [INFO] Guardando alteracoes locais no stash...
        git stash push -m "Auto-stash antes do pull"
    ) else (
        echo [INFO] Prosseguindo sem stash. Se houver conflito, o Git interrompera o pull.
    )
)

echo.
echo [1/2] Buscando atualizacoes de origin/%BRANCH_ATUAL%...
git pull origin %BRANCH_ATUAL%
if errorlevel 1 (
    echo.
    echo [ERRO] Falha ao executar git pull. Verifique sua conexao ou resolva eventuais conflitos.
    pause
    exit /b 1
)

REM 6. Restaura o stash caso tenha sido usado
if "%TEM_ALTERACOES%"=="1" (
    if /i "!USAR_STASH!"=="S" (
        echo [2/2] Restaurando suas alteracoes locais...
        git stash pop
        if errorlevel 1 (
            echo [AVISO] Conflito ao restaurar suas alteracoes locais. Verifique os arquivos marcados.
            pause
            exit /b 1
        )
    )
)

echo.
echo ==================================================
echo   Repositorio atualizado com sucesso!
echo ==================================================
pause
endlocal