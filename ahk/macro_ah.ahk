;
; Macro-ah (AutoHotKey v2)
;
; Halb-automatisches /ah-Listing. Per Strg+Leertaste gestartet.
; Details: siehe README.md im Repo-Root.
;
; Sicherheit: Esc oder Mausbewegung > 60px bricht ab.
; Kein Anti-Detection-Jitter.
;

#Requires AutoHotkey v2.0
#SingleInstance Force
SendMode "Event"
SetKeyDelay 25, 15
SetMouseDelay 8
CoordMode "Mouse", "Screen"
CoordMode "Pixel", "Screen"

; ---------- Globals ----------
global ConfigFile       := A_ScriptDir . "\config.ini"
global Points           := Map()
global PriceStr         := "1.20"
global AbortTolerance   := 60
global BaselineX        := 0
global BaselineY        := 0
global SacrificeIdx     := 0
global Cols             := 9
global Rows             := 4
global EmptySpreadThresh := 28

global CalibrationSteps := [
    Map("key", "ah_create_btn",       "desc", "/ah GUI: Button 'Auktion erstellen'"),
    Map("key", "ah_inv_top_left",     "desc", "/ah GUI: Oberster linker Inventar-Slot"),
    Map("key", "ah_inv_bottom_right", "desc", "/ah GUI: Unterer rechter Slot (Hotbar rechts)"),
    Map("key", "ah_green_check",      "desc", "/ah GUI: Gruener Haken in 'Stueck auswaehlen'"),
    Map("key", "ah_price_field",      "desc", "/ah GUI: Preis-Eingabefeld"),
    Map("key", "ah_confirm_btn",      "desc", "/ah GUI: Button 'Angebot erstellen'"),
    Map("key", "inv_top_left",        "desc", "Normales Inventar (E): oben links"),
    Map("key", "inv_bottom_right",    "desc", "Normales Inventar (E): Hotbar unten rechts")
]

; ---------- Entry ----------
Main()

Main() {
    LoadConfig()
    if !AllPointsCalibrated() {
        if !Calibrate() {
            return
        }
    }
    if !AskPrice() {
        return
    }
    ToolTip "Bereit. Wechsle zu Minecraft, dann Strg+Leertaste. Esc = Abbruch."
    SetTimer () => ToolTip(), -3500
}

AllPointsCalibrated() {
    for step in CalibrationSteps {
        if !Points.Has(step["key"]) {
            return false
        }
    }
    return true
}

; ---------- Config ----------
LoadConfig() {
    global Points
    Points := Map()
    if !FileExist(ConfigFile) {
        return
    }
    for step in CalibrationSteps {
        key := step["key"]
        try {
            xs := IniRead(ConfigFile, "points", key . "_x", "")
            ys := IniRead(ConfigFile, "points", key . "_y", "")
            if (xs != "" && ys != "") {
                Points[key] := [Integer(xs), Integer(ys)]
            }
        }
    }
}

SaveConfig() {
    for key, pos in Points {
        IniWrite pos[1], ConfigFile, "points", key . "_x"
        IniWrite pos[2], ConfigFile, "points", key . "_y"
    }
}

; ---------- Kalibrierung ----------
Calibrate() {
    cal := Gui("+AlwaysOnTop -MinimizeBox", "Macro-ah Kalibrierung")
    cal.SetFont("s10", "Segoe UI")
    lbl := cal.AddText("w420 h50", "")
    cal.AddText("xm w420 cGray", "Maus ueber die Stelle, dann LEERTASTE druecken. Esc = Abbruch.")
    status := cal.AddText("xm w300 cGray", "")
    cal.Show("w440 h120")

    aborted := false
    for idx, step in CalibrationSteps {
        lbl.Text := step["desc"]
        status.Text := "Schritt " . idx . "/" . CalibrationSteps.Length

        KeyWait "Space"
        KeyWait "Escape"
        loop {
            Sleep 21
        
            if GetKeyState("Escape", "P") {
                aborted := true
                break 2
            }
            if GetKeyState("Space", "P") {
                MouseGetPos &mx, &my
                Points[step["key"]] := [mx, my]
                KeyWait "Space"
                break
            }
        }
    }

    cal.Destroy()
    if (aborted) {
        return false
    }
    SaveConfig()
    return true
}

; ---------- Preis-Dialog ----------
AskPrice() {
    global PriceStr
    loop {
        res := InputBox("Preis pro Item (z.B. 1.20).`nNach OK: Strg+Leertaste in Minecraft.",
                        "Macro-ah", "w320 h150", PriceStr)
        if (res.Result != "OK") {
            return false
        }
        val := StrReplace(Trim(res.Value), ",", ".")
        if IsNumber(val) {
            PriceStr := Format("{:.2f}", Number(val))
            return true
        }
        MsgBox "Preis ungueltig. Beispiel: 1.20", "Fehler", "Iconx"
    }
}

; ---------- Abort / Safety ----------
ResetBaseline() {
    global BaselineX, BaselineY
    MouseGetPos &bx, &by
    BaselineX := bx
    BaselineY := by
}

CheckAbort() {
    MouseGetPos &mx, &my
    if (Abs(mx - BaselineX) > AbortTolerance || Abs(my - BaselineY) > AbortTolerance) {
        throw Error("Mausbewegung")
    }
    if GetKeyState("Escape", "P") {
        throw Error("Esc")
    }
}

Sleep2(ms) {
    endTime := A_TickCount + ms
    while (A_TickCount < endTime) {
        CheckAbort()
        Sleep Min(40, endTime - A_TickCount)
    }
}

MoveTo(x, y) {
    MouseMove x, y, 2
    ResetBaseline()
}

DoClick(pos, button := "Left", before := 120, after := 180) {
    Sleep2(before)
    MoveTo(pos[1], pos[2])
    Click button
    ResetBaseline()
    Sleep2(after)
}

; ---------- Pixel / Slot-Grid ----------
BuildGrid(topLeft, bottomRight) {
    grid := []
    x1 := topLeft[1], y1 := topLeft[2]
    x2 := bottomRight[1], y2 := bottomRight[2]
    dx := (x2 - x1) / (Cols - 1)
    dy := (y2 - y1) / (Rows - 1)
    loop Rows {
        rowIdx := A_Index - 1
        loop Cols {
            colIdx := A_Index - 1
            px := Round(x1 + colIdx * dx)
            py := Round(y1 + rowIdx * dy)
            grid.Push([px, py])
        }
    }
    return grid
}

IsSlotEmpty(cx, cy, radius := 6) {
    rMin := 255, rMax := 0
    gMin := 255, gMax := 0
    bMin := 255, bMax := 0
    offsets := [[-1,-1],[0,-1],[1,-1],[-1,0],[0,0],[1,0],[-1,1],[0,1],[1,1]]
    for off in offsets {
        px := cx + off[1] * radius
        py := cy + off[2] * radius
        color := PixelGetColor(px, py)
        r := (color >> 16) & 0xFF
        g := (color >> 8) & 0xFF
        b := color & 0xFF
        if (r < rMin)
            rMin := r
        if (r > rMax)
            rMax := r
        if (g < gMin)
            gMin := g
        if (g > gMax)
            gMax := g
        if (b < bMin)
            bMin := b
        if (b > bMax)
            bMax := b
    }
    spread := Max(rMax - rMin, gMax - gMin, bMax - bMin)
    return spread < EmptySpreadThresh
}

; ---------- Split-Phase ----------
SplitPhase() {
    grid := BuildGrid(Points["inv_top_left"], Points["inv_bottom_right"])

    Sleep2(300)
    Send "e"
    Sleep2(450)

    sourceIdx := -1
    for idx, pos in grid {
        realIdx := idx - 1
        if (realIdx = SacrificeIdx) {
            continue
        }
        if !IsSlotEmpty(pos[1], pos[2]) {
            sourceIdx := realIdx
            break
        }
    }
    if (sourceIdx = -1) {
        Send "e"
        throw Error("Kein Stack gefunden")
    }

    DoClick(grid[sourceIdx + 1], "Left", 100, 220)

    ; Rechtsklick-Drag ueber alle Slots ausser Opferslot
    targets := []
    for idx, pos in grid {
        realIdx := idx - 1
        if (realIdx = SacrificeIdx) {
            continue
        }
        targets.Push(pos)
    }

    MoveTo(targets[1][1], targets[1][2])
    Click "Right Down"
    try {
        loop targets.Length - 1 {
            CheckAbort()
            t := targets[A_Index + 1]
            MouseMove t[1], t[2], 2
            ResetBaseline()
        }
    } finally {
        Click "Right Up"
    }

    Sleep2(250)

    DoClick(grid[SacrificeIdx + 1], "Left", 100, 250)

    Send "e"
    Sleep2(500)
}

; ---------- /ah-Listing-Phase ----------
OpenAh() {
    Send "t"
    Sleep2(350)
    SendText "/ah"
    Sleep2(150)
    Send "{Enter}"
    Sleep2(900)
}

ListOne(slotPos) {
    DoClick(Points["ah_create_btn"], "Left", 120, 280)
    DoClick(slotPos,                  "Left", 100, 280)
    DoClick(Points["ah_green_check"], "Left", 100, 280)

    DoClick(Points["ah_price_field"], "Left", 100, 150)
    Send "^a"
    Sleep2(80)
    SendText PriceStr
    Sleep2(100)
    Send "{Enter}"
    Sleep2(280)

    DoClick(Points["ah_confirm_btn"], "Left", 120, 450)
}

ListingPhase() {
    grid := BuildGrid(Points["ah_inv_top_left"], Points["ah_inv_bottom_right"])

    filled := []
    for idx, pos in grid {
        realIdx := idx - 1
        if (realIdx = SacrificeIdx) {
            continue
        }
        if !IsSlotEmpty(pos[1], pos[2]) {
            filled.Push(pos)
        }
    }

    if (filled.Length = 0) {
        throw Error("Keine Items erkannt")
    }

    ToolTip "Liste " . filled.Length . " Items fuer " . PriceStr
    SetTimer () => ToolTip(), -2000

    for pos in filled {
        CheckAbort()
        ListOne(pos)
    }
}

; ---------- Hotkey ----------
^Space:: {
    RunMacro()
}

RunMacro() {
    ResetBaseline()
    try {
        SplitPhase()
        OpenAh()
        ResetBaseline()
        ListingPhase()
        ToolTip "Fertig."
        SetTimer () => ToolTip(), -2000
    } catch as e {
        try {
            Click "Right Up"
        } catch {
        }
        ToolTip "Abgebrochen: " . e.Message
        SetTimer () => ToolTip(), -2500
    }
}

; Esc wird NICHT remapped - CheckAbort() liest den physischen Tastenstatus.
; Minecraft kann Esc normal zum Menue-Schliessen nutzen.
