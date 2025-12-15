

# to enable
# > gsudo Set-ExecutionPolicy RemoteSigned
# to disable
# > gsudo Set-ExecutionPolicy AllSigned


# NOTE
# maybe use $([System.IO.Path]::PathSeparator) instead of ";"

if ($PSVersionTable.PSVersion.Major -lt 3) {
    Write-Error "PowerShell version < 3 is not supported"
} else {
    $env:PYTHONPATH=-join(
        "${PYTHONPATH}",
        ";$PSScriptRoot\pkg",
        ";$PSScriptRoot\test\pkg"
    )
    if ($env:PYTHONPATH.StartsWith(';')) {
        $env:PYTHONPATH = $env:PYTHONPATH.Remove(0,1) 
    }
}
