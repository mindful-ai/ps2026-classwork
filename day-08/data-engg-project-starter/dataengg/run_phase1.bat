@echo off
echo === Phase 1: Apply realistic mappings ===
python src\apply_mappings.py
if errorlevel 1 exit /b 1

echo.
echo === Phase 1: Run DuckDB SQL examples ===
python src\run_sql.py
