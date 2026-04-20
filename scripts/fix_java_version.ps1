# fix_java_version.ps1
$projectRoot = "C:\Users\hp\Pictures\Screenshots\jerome\git clone\karmic.gochara"

# 1. gradle.properties
$gradleProps = Join-Path $projectRoot "gradle.properties"
if (-not (Test-Path $gradleProps)) {
    New-Item -Path $gradleProps -ItemType File | Out-Null
}
$propLine = "org.gradle.java.home=C:\\Program Files\\Java\\jdk-17"
if (-not (Select-String -Path $gradleProps -Pattern "org.gradle.java.home" -Quiet)) {
    Add-Content $gradleProps $propLine
}

# 2. build.gradle files
Get-ChildItem -Path $projectRoot -Recurse -Filter "build.gradle" | ForEach-Object {
    $file = $_.FullName
    $content = [System.IO.File]::ReadAllText($file)
    if ($content.Contains("VERSION_21")) {
        $newContent = $content.Replace("VERSION_21", "VERSION_17")
        [System.IO.File]::WriteAllText($file, $newContent)
    }
}
Write-Host "Done."
