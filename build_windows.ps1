$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

python -m pip install -r requirements-build.txt
if ($LASTEXITCODE -ne 0) {
    throw "Could not install the Windows app build requirements."
}

$projectRoot = (Get-Location).Path
$dataGather = "$projectRoot\gather_rsvp;gather_rsvp"
$dataGuests = "$projectRoot\guests;guests"
$buildRoot = Join-Path $env:TEMP ("Nimoli-Windows-Build-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $buildRoot | Out-Null

try {
    python -m PyInstaller `
        --noconfirm `
        --clean `
        --console `
        --onefile `
        --icon "$projectRoot\guests\static\guests\app-icon.ico" `
        --name "Nimoli Bhandari Events" `
        --distpath "$projectRoot\windows-dist" `
        --workpath $buildRoot `
        --specpath $buildRoot `
        --add-data $dataGather `
        --add-data $dataGuests `
        --hidden-import guests.admin `
        --hidden-import guests.management.commands.seed_demo `
        --hidden-import guests.management.commands.remove_demo `
        --hidden-import guests.management.commands.send_whatsapp_campaigns `
        --collect-all openpyxl `
        --collect-all phonenumbers `
        --collect-all pycountry `
        --collect-all PIL `
        desktop_launcher.py
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller could not build the Windows app."
    }
}
finally {
    Remove-Item -LiteralPath $buildRoot -Recurse -Force -ErrorAction SilentlyContinue
}

Copy-Item WINDOWS-APP.txt "$projectRoot\windows-dist\README.txt" -Force
$zipPath = "$projectRoot\windows-dist\Nimoli-Bhandari-Events-Windows.zip"
$stagingPath = Join-Path $env:TEMP ("Nimoli-Bhandari-Events-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $stagingPath | Out-Null
try {
    Copy-Item "$projectRoot\windows-dist\Nimoli Bhandari Events.exe" "$stagingPath\Nimoli Bhandari Events.exe"
    Copy-Item "$projectRoot\windows-dist\README.txt" "$stagingPath\README.txt"
    Compress-Archive `
        -Path "$stagingPath\*" `
        -DestinationPath $zipPath `
        -Force
}
finally {
    Remove-Item -LiteralPath $stagingPath -Recurse -Force
}

Write-Output "Windows app: $projectRoot\windows-dist\Nimoli Bhandari Events.exe"
Write-Output "Download ZIP: $zipPath"
