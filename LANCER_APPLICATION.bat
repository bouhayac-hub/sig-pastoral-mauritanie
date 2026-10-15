@echo off
chcp 65001 > nul
title SIG Pastoral Mauritanie - Lancement Automatique
color 0A

echo ======================================================================
echo          SIG PASTORAL MAURITANIE - LANCEMENT AUTOMATIQUE
echo ======================================================================
echo.

echo [1/3] Verification de Python...
py --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PY_CMD=py
    goto :PYTHON_OK
)
python --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PY_CMD=python
    goto :PYTHON_OK
)

echo [ERREUR] Python n'est pas installe ou pas detecte dans le PATH !
echo.
pause
exit /b

:PYTHON_OK
echo Python detecte : OK (%PY_CMD%)
echo.

echo [2/3] Verification et installation automatique des modules requis...
%PY_CMD% -m pip install --quiet --upgrade pip
%PY_CMD% -m pip install -r requirements.txt

echo.
echo Modules installes et prets !
echo.

echo [3/3] Lancement de l'application SIG Pastoral dans votre navigateur...
%PY_CMD% -m streamlit run app.py

pause
