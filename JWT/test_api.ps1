<#
 Comprehensive API test script for Library System (PowerShell 5.1 compatible)
 - Tests admin and user flows
 - Covers login, verify, refresh, books CRUD, user borrow/return, logout, and negatives
 - Safe to re-run: creates and deletes a temporary test book
#>

$ErrorActionPreference = 'Stop'

$BASE = 'http://localhost:5000'
$pass = 0
$fail = 0

function Write-Title($text) {
    Write-Host "`n=== $text ===" -ForegroundColor Cyan
}

function Write-Step($text) {
    Write-Host "`n- $text" -ForegroundColor Yellow
}

function Result($name, $ok) {
    if ($ok) { $script:pass++ ; Write-Host "[PASS] $name" -ForegroundColor Green }
    else     { $script:fail++ ; Write-Host "[FAIL] $name" -ForegroundColor Red }
}

function Invoke-Api {
    param(
        [Parameter(Mandatory)] [string] $Path,
        [ValidateSet('GET','POST','PUT','DELETE')] [string] $Method = 'GET',
        [string] $Token,
        $Body
    )

    $headers = @{ 'Content-Type' = 'application/json' }
    if ($Token) { $headers['Authorization'] = "Bearer $Token" }
    $uri = if ($Path -match '^https?://') { $Path } else { "$BASE$Path" }

    $raw = $null; $status = $null
    try {
        if ($PSBoundParameters.ContainsKey('Body') -and $null -ne $Body) {
            $json = $Body | ConvertTo-Json -Depth 6
            $resp = Invoke-WebRequest -Uri $uri -Method $Method -Headers $headers -Body $json
        } else {
            $resp = Invoke-WebRequest -Uri $uri -Method $Method -Headers $headers
        }
        $status = [int]$resp.StatusCode
        $raw = $resp.Content
    } catch {
        try { $status = [int]$_.Exception.Response.StatusCode.Value__ } catch { $status = 0 }
        try {
            $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
            $raw = $reader.ReadToEnd(); $reader.Close()
        } catch { $raw = '' }
    }

    $data = $null
    if ($raw -and ($raw.Trim().StartsWith('{') -or $raw.Trim().StartsWith('['))) {
        try { $data = $raw | ConvertFrom-Json } catch { $data = $null }
    }

    return [pscustomobject]@{ Status = $status; Raw = $raw; Data = $data }
}

function Assert-Status {
    param(
        [Parameter(Mandatory)] $Resp,
        [Parameter(Mandatory)] [int[]] $Expected,
        [string] $Name = 'assert'
    )
    $ok = $Expected -contains [int]$Resp.Status
    if (-not $ok) {
        Write-Host ("Expected {0}, got {1}" -f ($Expected -join ','), $Resp.Status) -ForegroundColor DarkYellow
        if ($Resp.Raw) { Write-Host $Resp.Raw -ForegroundColor DarkGray }
    }
    Result $Name $ok
    return $ok
}

function Login($username, $password) {
    Write-Step "Login as $username"
    $resp = Invoke-Api -Path '/api/sessions' -Method 'POST' -Body @{ username=$username; password=$password }
    Assert-Status $resp @(200) "Login $username"
    return $resp
}

function Refresh-AccessToken($refreshToken) {
    Write-Step "Refresh access token"
    $resp = Invoke-Api -Path '/api/sessions/refresh' -Method 'POST' -Body @{ refresh_token = $refreshToken }
    Assert-Status $resp @(200,401) "Refresh token"
    return $resp
}

# --- Health check ---
Write-Title 'Health check'
$health = Invoke-Api -Path '/'
if ($health.Status -eq 0) {
    Write-Host "Cannot connect to $BASE. Please start the backend: python backend/server.py" -ForegroundColor Red
    exit 1
}
Assert-Status $health @(200) 'Root reachable'

# --- Admin flow ---
Write-Title 'Admin flow'
$adminLogin = Login 'admin' 'admin123'
$adminData = $adminLogin.Data
$adminAT = $adminData.data.access_token
$adminRT = $adminData.data.refresh_token
$adminUser = $adminData.data

$meA = Invoke-Api -Path '/api/sessions/me' -Method 'GET' -Token $adminAT
Assert-Status $meA @(200) 'Verify admin token'

$stats = Invoke-Api -Path '/api/statistics' -Method 'GET' -Token $adminAT
Assert-Status $stats @(200) 'Get statistics'

$booksA = Invoke-Api -Path '/api/books' -Method 'GET' -Token $adminAT
Assert-Status $booksA @(200) 'List books (admin)'

# Create a test book
$testKey = 'TEST-' + [Guid]::NewGuid().ToString('N').Substring(0,8)
$create = Invoke-Api -Path '/api/books' -Method 'POST' -Token $adminAT -Body @{ 
    book_key = $testKey; title = "Test Book $testKey"; author = 'Test Author'; cover_url=''; quantity = 2 
}
Assert-Status $create @(201,409) 'Create book'
$createdId = $null
if ($create.Status -eq 201) { $createdId = $create.Data.data.id } else {
    # If already exists (unlikely), try to find it
    $existingList = Invoke-Api -Path '/api/books' -Method 'GET' -Token $adminAT
    $createdId = ($existingList.Data.data | Where-Object { $_.book_key -eq $testKey } | Select-Object -First 1).id
}

if ($createdId) {
    $detail = Invoke-Api -Path "/api/books/$createdId" -Method 'GET' -Token $adminAT
    Assert-Status $detail @(200) 'Get created book detail'

    $update = Invoke-Api -Path "/api/books/$createdId" -Method 'PUT' -Token $adminAT -Body @{ quantity = 3 }
    Assert-Status $update @(200) 'Update book quantity'
}

# --- User flow ---
Write-Title 'User flow'
$userLogin = Login 'user' 'user123'
$userData = $userLogin.Data
$userAT = $userData.data.access_token
$userRT = $userData.data.refresh_token
$user = $userData.data

$meU = Invoke-Api -Path '/api/sessions/me' -Method 'GET' -Token $userAT
Assert-Status $meU @(200) 'Verify user token'

$booksU = Invoke-Api -Path '/api/books' -Method 'GET' -Token $userAT
Assert-Status $booksU @(200) 'List books (user)'

# Pick first available book that's not our temporary test (prefer existing samples)
$bookToBorrow = $booksU.Data.data | Where-Object { $_.available -gt 0 } | Select-Object -First 1
if (-not $bookToBorrow -and $createdId) {
    $detail2 = Invoke-Api -Path "/api/books/$createdId" -Method 'GET' -Token $userAT
    $bookToBorrow = $detail2.Data.data
}

if ($bookToBorrow) {
    $borrow = Invoke-Api -Path "/api/users/$($user.id)/borrowed-books" -Method 'POST' -Token $userAT -Body @{ book_id = $bookToBorrow.id }
    Assert-Status $borrow @(201,409) 'Borrow a book'

    $borrowedList = Invoke-Api -Path "/api/users/$($user.id)/borrowed-books" -Method 'GET' -Token $userAT
    Assert-Status $borrowedList @(200) 'List my borrowed books'

    # Return book (use library book id in route)
    $return = Invoke-Api -Path "/api/users/$($user.id)/borrowed-books/$($bookToBorrow.id)" -Method 'DELETE' -Token $userAT
    Assert-Status $return @(200,404) 'Return the borrowed book'
} else {
    Result 'Borrow flow (no available book found)' $false
}

# Negative: user tries to read another user's borrowed list
$otherId = [int]$user.id + 999
$forbidden = Invoke-Api -Path "/api/users/$otherId/borrowed-books" -Method 'GET' -Token $userAT
Assert-Status $forbidden @(403) "User cannot access others' borrowed books"

# Refresh flow with user refresh token
$ref = Refresh-AccessToken $userRT
if ($ref.Status -eq 200) {
    $newAT = $ref.Data.data.access_token
    $verifyNew = Invoke-Api -Path '/api/sessions/me' -Method 'GET' -Token $newAT
    Assert-Status $verifyNew @(200) 'Verify new access token after refresh'
} else {
    Result 'Refresh token should succeed (user)' $false
}

# Logout user (revoke refresh and blacklist access)
Write-Step 'Logout user'
$logoutU = Invoke-Api -Path '/api/sessions' -Method 'DELETE' -Token $userAT -Body @{ refresh_token = $userRT }
Assert-Status $logoutU @(200) 'User logout'

# Using old access token should now fail due to blacklist
$meAfterLogout = Invoke-Api -Path '/api/sessions/me' -Method 'GET' -Token $userAT
Assert-Status $meAfterLogout @(401) 'Access token invalid after logout'

# Refresh again should fail (revoked refresh token)
$refAfterLogout = Refresh-AccessToken $userRT
Assert-Status $refAfterLogout @(401) 'Refresh denied after logout'

# Cleanup: delete test book (if created)
if ($createdId) {
    Write-Step "Cleanup: delete test book $createdId"
    $del = Invoke-Api -Path "/api/books/$createdId" -Method 'DELETE' -Token $adminAT
    Assert-Status $del @(200,404) 'Delete test book'
}

# Admin logout (optional)
$logoutA = Invoke-Api -Path '/api/sessions' -Method 'DELETE' -Token $adminAT -Body @{ refresh_token = $adminRT }
Assert-Status $logoutA @(200) 'Admin logout'

Write-Title 'Summary'
Write-Host ("Passed: {0}  Failed: {1}" -f $pass, $fail) -ForegroundColor Cyan
if ($fail -gt 0) { exit 2 } else { exit 0 }

