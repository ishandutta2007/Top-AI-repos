# Description: Fixes the serial numbers in the README.md table to be in ascending order starting from 1.
# Usage: powershell.exe -NoProfile -ExecutionPolicy Bypass -File fix_serials.ps1
# This script ensures UTF-8 encoding (without BOM) is preserved.

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$filePath = "README.md"

if (Test-Path $filePath) {
    $content = [IO.File]::ReadAllText($filePath, [System.Text.Encoding]::UTF8)
    $lines = $content -split "\r?\n"
    $newLines = New-Object System.Collections.Generic.List[string]
    $inBody = $false
    $serial = 1

    foreach ($line in $lines) {
        if ($line -like "*|---|---|---|---|---|---|---|*") {
            $newLines.Add($line)
            $inBody = $true
            continue
        }
        if ($inBody) {
            if ($line.Trim().StartsWith("|")) {
                # Update the first column with the serial number
                $newLine = $line -replace "^\|[^|]+\|", "|$serial|"
                $serial++
                $newLines.Add($newLine)
            } elseif ($line.Trim() -eq "") {
                $newLines.Add($line)
            } else {
                $inBody = $false
                $newLines.Add($line)
            }
        } else {
            $newLines.Add($line)
        }
    }

    [IO.File]::WriteAllLines($filePath, $newLines, $utf8NoBom)
    Write-Host "Serial numbers fixed in $filePath"
} else {
    Write-Error "$filePath not found."
}
