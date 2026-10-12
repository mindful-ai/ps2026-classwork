@echo off
echo ==========================================
echo E-Commerce Data Engineering - Phase 6
echo ==========================================
python src/build_ml_ready.py
if errorlevel 1 exit /b 1
python src/inspect_ml_ready.py
pytest -q src/test_phase6.py
