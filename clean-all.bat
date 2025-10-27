@echo off
echo Cleaning both input-xml and output-xml directories (keeping .gitkeep files)...
echo.
call clean-input.bat
echo.
call clean-output.bat
echo.
echo All directories cleaned!