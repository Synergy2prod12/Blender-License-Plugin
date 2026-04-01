bl_info = {
    "name": "Blender License Manager",
    "description": "Blender registration lock & free trial",
    "author": "Arjed Lade",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "location": "View3D",
    "warning": "April Fools!",
    "wiki_url": "",
    "tracker_url": "",
    "category": "System"
}

import bpy
import blf
import os
import sys
import subprocess
import tempfile
import json
import time
from datetime import datetime, timedelta

# --- State Management ---
PRANK_STATE_FILE = os.path.join(tempfile.gettempdir(), "blender_license_state.json")

def get_state():
    if os.path.exists(PRANK_STATE_FILE):
        try:
            with open(PRANK_STATE_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {"status": "unregistered", "trial_start": None}

def save_state(state):
    try:
        with open(PRANK_STATE_FILE, "w") as f:
            json.dump(state, f)
    except:
        pass

def get_trial_days_left():
    state = get_state()
    if state["status"] == "trial" and state["trial_start"]:
        start_time = datetime.fromisoformat(state["trial_start"])
        expiry_time = start_time + timedelta(days=7)
        now = datetime.now()
        days_left = (expiry_time - now).days
        return max(0, days_left)
    return 0

def check_trial_expired():
    state = get_state()
    if state["status"] == "trial" and state["trial_start"]:
        start_time = datetime.fromisoformat(state["trial_start"])
        if datetime.now() > start_time + timedelta(days=7):
            return True
    return False

def self_destruct():
    plugin_path = os.path.abspath(__file__)
    try:
        if os.path.exists(plugin_path):
            os.remove(plugin_path)
    except:
        pass
    if os.path.exists(PRANK_STATE_FILE):
        try:
            os.remove(PRANK_STATE_FILE)
        except:
            pass

# --- UI and PowerShell ---
def show_activation_window():
    if sys.platform != 'win32':
        return
        
    state = get_state()
    if state["status"] == "activated":
        return
        
    # If trial is expired, instantly self destruct so the prank ends after 7 days automatically
    if check_trial_expired():
        self_destruct()
        return


    ps_script = r"""
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

[System.Windows.Forms.Application]::EnableVisualStyles()

$form = New-Object System.Windows.Forms.Form
$form.Text = "Blender License Manager"
$form.Size = New-Object System.Drawing.Size(800, 500)
$form.StartPosition = "CenterScreen"
$form.FormBorderStyle = "None"
$form.BackColor = [System.Drawing.Color]::White
$form.TopMost = $true

# Exit gracefully so blender can un-minimize if user backs out
$form.Add_FormClosing({
    if ($form.DialogResult -ne [System.Windows.Forms.DialogResult]::OK) {
        [Environment]::Exit(3)
    }
})

# ================= PANELS ================= #
$pnlLoading = New-Object System.Windows.Forms.Panel
$pnlLoading.Size = New-Object System.Drawing.Size(800, 500)
$pnlLoading.BackColor = [System.Drawing.ColorTranslator]::FromHtml('#2b2b2b')
$pnlLoading.Dock = "Fill"
$form.Controls.Add($pnlLoading)

$pnlOptions = New-Object System.Windows.Forms.Panel
$pnlOptions.Size = New-Object System.Drawing.Size(800, 500)
$pnlOptions.BackColor = [System.Drawing.Color]::White
$pnlOptions.Dock = "Fill"
$pnlOptions.Visible = $false
$form.Controls.Add($pnlOptions)

$pnlSerial = New-Object System.Windows.Forms.Panel
$pnlSerial.Size = New-Object System.Drawing.Size(800, 500)
$pnlSerial.BackColor = [System.Drawing.Color]::White
$pnlSerial.Dock = "Fill"
$pnlSerial.Visible = $false
$form.Controls.Add($pnlSerial)

# --- Loading Panel Design ---
$lblLoadingTitle = New-Object System.Windows.Forms.Label
$lblLoadingTitle.Text = "Blender Foundation`nLicense Verification..."
$lblLoadingTitle.Font = New-Object System.Drawing.Font("Segoe UI", 28, [System.Drawing.FontStyle]::Regular)
$lblLoadingTitle.ForeColor = [System.Drawing.Color]::White
$lblLoadingTitle.AutoSize = $true
$lblLoadingTitle.Location = New-Object System.Drawing.Point(50, 160)
$pnlLoading.Controls.Add($lblLoadingTitle)

$progressBar = New-Object System.Windows.Forms.ProgressBar
$progressBar.Size = New-Object System.Drawing.Size(700, 4)
$progressBar.Location = New-Object System.Drawing.Point(50, 300)
$progressBar.Style = "Marquee"
$pnlLoading.Controls.Add($progressBar)

# --- Shared UI Features ---
function Add-Sidebar($parentPanel) {
    $pnlSidebar = New-Object System.Windows.Forms.Panel
    $pnlSidebar.Size = New-Object System.Drawing.Size(300, 500)
    $pnlSidebar.BackColor = [System.Drawing.ColorTranslator]::FromHtml('#e0792a')
    $pnlSidebar.Dock = "Left"
    $parentPanel.Controls.Add($pnlSidebar)

    $lblSideLogo = New-Object System.Windows.Forms.Label
    $lblSideLogo.Text = "Blender`nLicense`nManager"
    $lblSideLogo.Font = New-Object System.Drawing.Font("Segoe UI", 32, [System.Drawing.FontStyle]::Bold)
    $lblSideLogo.ForeColor = [System.Drawing.Color]::White
    $lblSideLogo.AutoSize = $true
    $lblSideLogo.Location = New-Object System.Drawing.Point(30, 40)
    $pnlSidebar.Controls.Add($lblSideLogo)
    return $pnlSidebar
}

function Add-CloseBtn($parentPanel) {
    $btnCloseTop = New-Object System.Windows.Forms.Button
    $btnCloseTop.Text = "X"
    $btnCloseTop.Font = New-Object System.Drawing.Font("Segoe UI", 12, [System.Drawing.FontStyle]::Bold)
    $btnCloseTop.Size = New-Object System.Drawing.Size(40, 40)
    $btnCloseTop.Location = New-Object System.Drawing.Point(760, 0)
    $btnCloseTop.FlatStyle = "Flat"
    $btnCloseTop.FlatAppearance.BorderSize = 0
    $btnCloseTop.BackColor = [System.Drawing.Color]::White
    $btnCloseTop.ForeColor = [System.Drawing.Color]::Gray
    $btnCloseTop.Add_Click({ [Environment]::Exit(3) })
    $parentPanel.Controls.Add($btnCloseTop)
}

Add-Sidebar $pnlOptions | Out-Null
Add-CloseBtn $pnlOptions

Add-Sidebar $pnlSerial | Out-Null
Add-CloseBtn $pnlSerial

# --- Options Panel Design ---
$lblOptTitle = New-Object System.Windows.Forms.Label
$lblOptTitle.Text = "Let's Get Started"
$lblOptTitle.Font = New-Object System.Drawing.Font("Segoe UI", 24, [System.Drawing.FontStyle]::Regular)
$lblOptTitle.ForeColor = [System.Drawing.ColorTranslator]::FromHtml('#333333')
$lblOptTitle.AutoSize = $true
$lblOptTitle.Location = New-Object System.Drawing.Point(340, 40)
$pnlOptions.Controls.Add($lblOptTitle)

$lblOptSub = New-Object System.Windows.Forms.Label
$lblOptSub.Text = "Your Blender software is currently not registered.`nSelect an option below to activate your product."
$lblOptSub.Font = New-Object System.Drawing.Font("Segoe UI", 11)
$lblOptSub.ForeColor = [System.Drawing.Color]::Gray
$lblOptSub.AutoSize = $true
$lblOptSub.Location = New-Object System.Drawing.Point(345, 90)
$pnlOptions.Controls.Add($lblOptSub)

function Create-OptionButton {
    param($text, $x, $y, $clickAction)
    $btn = New-Object System.Windows.Forms.Button
    $btn.Text = $text
    $btn.Font = New-Object System.Drawing.Font("Segoe UI", 10, [System.Drawing.FontStyle]::Bold)
    $btn.Size = New-Object System.Drawing.Size(205, 90)
    $btn.Location = New-Object System.Drawing.Point($x, $y)
    $btn.FlatStyle = "Flat"
    $btn.BackColor = [System.Drawing.ColorTranslator]::FromHtml('#f8f8f8')
    $btn.FlatAppearance.BorderColor = [System.Drawing.ColorTranslator]::FromHtml('#dddddd')
    $btn.TextAlign = "MiddleCenter"
    $btn.Add_Click($clickAction)
    return $btn
}

$btnSignIn = Create-OptionButton "Sign In with Blender ID" 340 140 {
    [System.Windows.Forms.MessageBox]::Show("Connection to Blender ID Server failed (Error 0x800AD1).`nPlease check your network connection or firewall.", "Server Unreachable", 0, 16)
}
$btnSerialOpt = Create-OptionButton "Enter a Serial Number" 555 140 {
    $pnlOptions.Visible = $false
    $pnlSerial.Visible = $true
}
$btnNetwork = Create-OptionButton "Use a Network License" 340 240 {
    [System.Windows.Forms.MessageBox]::Show("No network license server found on your local subnet.`nPlease specify a server manually or use a different method.", "Network License Error", 0, 16)
}
$btnPurchase = Create-OptionButton "Purchase Blender" 555 240 {
    [System.Diagnostics.Process]::Start("https://fund.blender.org/")
}

$btnTrial = New-Object System.Windows.Forms.Button
$btnTrial.Text = "___TRIAL_TEXT___"
$btnTrial.Font = New-Object System.Drawing.Font("Segoe UI", 12, [System.Drawing.FontStyle]::Bold)
$btnTrial.Size = New-Object System.Drawing.Size(420, 50)
$btnTrial.Location = New-Object System.Drawing.Point(340, 350)
$btnTrial.FlatStyle = "Flat"
$btnTrial.BackColor = [System.Drawing.ColorTranslator]::FromHtml('#2b2b2b')
$btnTrial.ForeColor = [System.Drawing.Color]::White
$btnTrial.FlatAppearance.BorderSize = 0
$btnTrial.Add_Click({
    [System.Windows.Forms.MessageBox]::Show("Your 7-day free trial has started.`n`nEnjoy your evaluation period.", "Trial Started", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Information)
    $form.DialogResult = [System.Windows.Forms.DialogResult]::OK
    [Environment]::Exit(1) # Code 1 = Start Trial
})
$pnlOptions.Controls.Add($btnTrial)

$pnlOptions.Controls.Add($btnSignIn)
$pnlOptions.Controls.Add($btnSerialOpt)
$pnlOptions.Controls.Add($btnNetwork)
$pnlOptions.Controls.Add($btnPurchase)

# --- Serial Panel Design ---
$lblSerTitle = New-Object System.Windows.Forms.Label
$lblSerTitle.Text = "Product License Activation"
$lblSerTitle.Font = New-Object System.Drawing.Font("Segoe UI", 24, [System.Drawing.FontStyle]::Regular)
$lblSerTitle.ForeColor = [System.Drawing.ColorTranslator]::FromHtml('#333333')
$lblSerTitle.AutoSize = $true
$lblSerTitle.Location = New-Object System.Drawing.Point(340, 40)
$pnlSerial.Controls.Add($lblSerTitle)

$lblEmail = New-Object System.Windows.Forms.Label
$lblEmail.Text = "Registered Email:"
$lblEmail.Font = New-Object System.Drawing.Font("Segoe UI", 9, [System.Drawing.FontStyle]::Bold)
$lblEmail.AutoSize = $true
$lblEmail.Location = New-Object System.Drawing.Point(340, 110)
$pnlSerial.Controls.Add($lblEmail)

$txtEmail = New-Object System.Windows.Forms.TextBox
$txtEmail.Font = New-Object System.Drawing.Font("Segoe UI", 12)
$txtEmail.Size = New-Object System.Drawing.Size(420, 30)
$txtEmail.Location = New-Object System.Drawing.Point(340, 130)
$pnlSerial.Controls.Add($txtEmail)

$lblOrg = New-Object System.Windows.Forms.Label
$lblOrg.Text = "Organization:"
$lblOrg.Font = New-Object System.Drawing.Font("Segoe UI", 9, [System.Drawing.FontStyle]::Bold)
$lblOrg.AutoSize = $true
$lblOrg.Location = New-Object System.Drawing.Point(340, 180)
$pnlSerial.Controls.Add($lblOrg)

$txtOrg = New-Object System.Windows.Forms.TextBox
$txtOrg.Font = New-Object System.Drawing.Font("Segoe UI", 12)
$txtOrg.Size = New-Object System.Drawing.Size(420, 30)
$txtOrg.Location = New-Object System.Drawing.Point(340, 200)
$pnlSerial.Controls.Add($txtOrg)

$lblKey = New-Object System.Windows.Forms.Label
$lblKey.Text = "Serial Number:"
$lblKey.Font = New-Object System.Drawing.Font("Segoe UI", 9, [System.Drawing.FontStyle]::Bold)
$lblKey.AutoSize = $true
$lblKey.Location = New-Object System.Drawing.Point(340, 250)
$pnlSerial.Controls.Add($lblKey)

$txtKey = New-Object System.Windows.Forms.TextBox
$txtKey.Font = New-Object System.Drawing.Font("Courier New", 14)
$txtKey.Size = New-Object System.Drawing.Size(420, 30)
$txtKey.Location = New-Object System.Drawing.Point(340, 270)
$pnlSerial.Controls.Add($txtKey)

$btnBack = New-Object System.Windows.Forms.Button
$btnBack.Text = "Back"
$btnBack.Font = New-Object System.Drawing.Font("Segoe UI", 10)
$btnBack.Size = New-Object System.Drawing.Size(100, 40)
$btnBack.Location = New-Object System.Drawing.Point(340, 350)
$btnBack.BackColor = [System.Drawing.ColorTranslator]::FromHtml('#e1e1e1')
$btnBack.FlatStyle = "Flat"
$btnBack.FlatAppearance.BorderSize = 0
$btnBack.Add_Click({
    $pnlSerial.Visible = $false
    $pnlOptions.Visible = $true
})
$pnlSerial.Controls.Add($btnBack)

$btnActivate = New-Object System.Windows.Forms.Button
$btnActivate.Text = "Activate"
$btnActivate.Size = New-Object System.Drawing.Size(120, 40)
$btnActivate.Location = New-Object System.Drawing.Point(640, 350)
$btnActivate.BackColor = [System.Drawing.ColorTranslator]::FromHtml('#e0792a')
$btnActivate.ForeColor = [System.Drawing.Color]::White
$btnActivate.FlatStyle = "Flat"
$btnActivate.FlatAppearance.BorderSize = 0
$btnActivate.Font = New-Object System.Drawing.Font("Segoe UI", 10, [System.Drawing.FontStyle]::Bold)
$btnActivate.Add_Click({
    $k = $txtKey.Text.Trim()
    if ($k.ToUpper() -eq "APRILFOOLS") {
        [System.Windows.Forms.MessageBox]::Show("April Fools!`n`nThe Blender Registration prank will now self-destruct. Enjoy your modeling!", "Bypass Successful", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Information)
        $form.DialogResult = [System.Windows.Forms.DialogResult]::OK
        [Environment]::Exit(2) # Code 2 = Activate & Self Destruct
    } else {
        [System.Windows.Forms.MessageBox]::Show("Invalid Product Key (Error 0x80041003).`nPlease ensure your serial number is entered correctly.", "Activation Error", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Error)
    }
})
$pnlSerial.Controls.Add($btnActivate)


$timer = New-Object System.Windows.Forms.Timer
$timer.Interval = 3000
$timer.Add_Tick({
    $timer.Stop()
    $pnlLoading.Visible = $false
    $pnlOptions.Visible = $true
})

$form.Add_Shown({
    $timer.Start()
})

$form.ShowDialog() | Out-Null
"""
    
    trial_left = get_trial_days_left()
    if state["status"] == "trial":
        btn_text = f"➔  Continue Free Trial ({trial_left} Days Left)"
    else:
        btn_text = "➔  Start 7-Day Free Trial"
        
    ps_script = ps_script.replace("___TRIAL_TEXT___", btn_text)
    
    script_path = os.path.join(tempfile.gettempdir(), "blender_prank_modern.ps1")
    with open(script_path, "w", encoding="utf-8-sig") as f:
        f.write(ps_script)
        
    try:
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-STA", "-ExecutionPolicy", "Bypass", "-WindowStyle", "Hidden", "-File", script_path],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        ret = result.returncode
        if ret == 1:
            save_state({"status": "trial", "trial_start": datetime.now().isoformat()})
        elif ret == 2:
            save_state({"status": "activated", "trial_start": None})
            self_destruct()
        elif ret == 3:
            # Quit blender immediately
            os._exit(0)
            
    except Exception as e:
        print("Activation prank failed:", e)


# --- Viewport HUD ---
draw_handle = None

def draw_hud():
    state = get_state()
    if state["status"] == "activated":
        return
        
    font_id = 0
    
    # Draw Background box top right
    width = bpy.context.region.width
    height = bpy.context.region.height
    
    # Move to Bottom Left
    x = 30
    y = 60
    
    # Main Warning Text
    blf.position(font_id, x, y, 0)
    blf.size(font_id, 24)
    if state["status"] == "trial":
        days = get_trial_days_left()
        blf.color(font_id, 1.0, 0.8, 0.0, 1.0) # Yellow text
        blf.draw(font_id, f"EVALUATION COPY - {days} Days Left in Free Trial")
    else:
        blf.color(font_id, 1.0, 0.2, 0.2, 1.0) # Red text
        blf.draw(font_id, "BLENDER SOFTWARE UNREGISTERED")
        
    # Subtext
    blf.position(font_id, x, y - 25, 0)
    blf.size(font_id, 14)
    blf.color(font_id, 0.8, 0.8, 0.8, 1.0)
    
    if state["status"] == "trial":
        blf.draw(font_id, "Please purchase a valid license to avoid disruption.")
    else:
        blf.draw(font_id, "Enter a valid serial key on launch to remove restrictions.")

# --- Registration Hooks ---
class PRANK_OT_dummy(bpy.types.Operator):
    bl_idname = "wm.prank_dummy"
    bl_label = "Prank Dummy"
    def execute(self, context):
        return {'FINISHED'}

def register():
    bpy.utils.register_class(PRANK_OT_dummy)
    if hasattr(bpy.app.timers, "register"):
        bpy.app.timers.register(show_activation_window, first_interval=0.5)
    else:
        show_activation_window()
        
    global draw_handle
    draw_handle = bpy.types.SpaceView3D.draw_handler_add(draw_hud, (), 'WINDOW', 'POST_PIXEL')

def unregister():
    bpy.utils.unregister_class(PRANK_OT_dummy)
    
    global draw_handle
    if draw_handle is not None:
        bpy.types.SpaceView3D.draw_handler_remove(draw_handle, 'WINDOW')
        draw_handle = None

if __name__ == "__main__":
    register()
