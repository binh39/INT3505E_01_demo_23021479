# PowerShell Script để test API

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Library Management API Test Script" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:5000"

# Test 1: Login as Admin
Write-Host "1. Testing Admin Login..." -ForegroundColor Yellow
$adminLogin = @{
    username = "admin"
    password = "admin123"
} | ConvertTo-Json

try {
    $adminResponse = Invoke-RestMethod -Uri "$baseUrl/api/sessions" -Method POST -Body $adminLogin -ContentType "application/json"
    Write-Host "Success: Admin login successful" -ForegroundColor Green
    Write-Host "  Role: $($adminResponse.data.role)" -ForegroundColor Gray
    $adminToken = $adminResponse.data.token
    $adminHeaders = @{
        "Authorization" = "Bearer $adminToken"
    }
} catch {
    Write-Host "Error: Admin login failed" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit
}
Write-Host ""

# Test 2: Verify Token
Write-Host "2. Testing Token Verification..." -ForegroundColor Yellow
try {
    $verifyResponse = Invoke-RestMethod -Uri "$baseUrl/api/sessions/me" -Headers $adminHeaders
    Write-Host "Success: Token is valid" -ForegroundColor Green
    Write-Host "  User: $($verifyResponse.data.username)" -ForegroundColor Gray
} catch {
    Write-Host "Error: Token verification failed" -ForegroundColor Red
}
Write-Host ""

# Test 3: Get Statistics
Write-Host "3. Testing Get Statistics..." -ForegroundColor Yellow
try {
    $statsResponse = Invoke-RestMethod -Uri "$baseUrl/api/statistics" -Headers $adminHeaders
    Write-Host "Success: Statistics retrieved" -ForegroundColor Green
    Write-Host "  Total Books: $($statsResponse.data.library.total_unique_books)" -ForegroundColor Gray
    Write-Host "  Total Copies: $($statsResponse.data.library.total_copies)" -ForegroundColor Gray
} catch {
    Write-Host "Error: Get statistics failed" -ForegroundColor Red
}
Write-Host ""

# Test 4: Get All Books
Write-Host "4. Testing Get All Books..." -ForegroundColor Yellow
try {
    $booksResponse = Invoke-RestMethod -Uri "$baseUrl/api/books" -Headers $adminHeaders
    Write-Host "Success: Books retrieved" -ForegroundColor Green
    Write-Host "  Total: $($booksResponse.meta.total_count)" -ForegroundColor Gray
    Write-Host "  Page: $($booksResponse.meta.page) / $($booksResponse.meta.total_pages)" -ForegroundColor Gray
} catch {
    Write-Host "Error: Get books failed" -ForegroundColor Red
}
Write-Host ""

# Test 5: Create New Book
Write-Host "5. Testing Create Book..." -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyyMMddHHmmss"
$newBook = @{
    book_key = "TEST_$timestamp"
    title = "Test Book - PowerShell"
    author = "Test Author"
    cover_url = "https://via.placeholder.com/200x300"
    quantity = 3
} | ConvertTo-Json

try {
    $createResponse = Invoke-RestMethod -Uri "$baseUrl/api/books" -Method POST -Headers $adminHeaders -Body $newBook -ContentType "application/json"
    Write-Host "Success: Book created" -ForegroundColor Green
    Write-Host "  ID: $($createResponse.data.id)" -ForegroundColor Gray
    Write-Host "  Title: $($createResponse.data.title)" -ForegroundColor Gray
    $testBookId = $createResponse.data.id
} catch {
    Write-Host "Error: Create book failed" -ForegroundColor Red
}
Write-Host ""

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Basic tests completed!" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan

