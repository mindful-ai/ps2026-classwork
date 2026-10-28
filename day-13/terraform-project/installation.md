winget install --id Hashicorp.Terraform -e
----------------------------------------------------------------------------------------------

powershell -NoProfile -Command "Get-ChildItem 'C:\Program Files','C:\Program Files (x86)',\"$env:LOCALAPPDATA\Microsoft\WinGet\Packages\" -Filter terraform.exe -Recurse -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName"


setx PATH "%PATH%;C:\Users\mindf\AppData\Local\Microsoft\WinGet\Packages\Hashicorp.Terraform_Microsoft.Winget.Source_8wekyb3d8bbwe"