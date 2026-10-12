@echo off
echo ==========================================
echo E-Commerce Data Engineering - Phase 5
echo ==========================================
python src/production_pipeline.py
if errorlevel 1 (
  echo PHASE 5 PIPELINE FAILED
  exit /b 1
)
echo PHASE 5 PIPELINE SUCCESS
