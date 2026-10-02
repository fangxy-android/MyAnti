# Codex Desktop Pet - PowerShell Helper Functions
# 可以将此文件中的函数添加到你的 PowerShell $PROFILE 中：
# . "D:\Project\MyAnti\hooks\Invoke-PetState.ps1"

$global:PetCliPath = "D:\Project\MyAnti\pet-cli.py"

function pet-status {
    python $global:PetCliPath status
}

function pet-working {
    param([string]$Message = "正在处理任务...")
    python $global:PetCliPath working $Message
}

function pet-done {
    param([string]$Message = "任务执行成功！")
    python $global:PetCliPath done $Message
}

function pet-error {
    param([string]$Message = "执行过程中遇到错误！")
    python $global:PetCliPath error $Message
}

function pet-thinking {
    param([string]$Message = "正在思考分析...")
    python $global:PetCliPath thinking $Message
}

function pet-waiting {
    param([string]$Message = "等待用户确认...")
    python $global:PetCliPath waiting $Message
}

function pet-say {
    param([string]$Message = "你好呀！")
    python $global:PetCliPath say $Message
}

function pet-char {
    param([string]$Character = "dewey")
    python $global:PetCliPath char $Character
}
