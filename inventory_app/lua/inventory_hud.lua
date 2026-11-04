-- inventory_hud.lua
-- On-device inventory management & alert HUD for Brilliant Labs Frame and Halo glasses.

local is_halo = (frame.HARDWARE_VERSION == "halo")

-- Color definitions
local COLOR_BG = 0x000000
local COLOR_WHITE = is_halo and 0xFFFFFF or 'WHITE'
local COLOR_GREEN = is_halo and 0x22DD44 or 'GREEN'
local COLOR_YELLOW = is_halo and 0xFFCC00 or 'YELLOW'
local COLOR_RED = is_halo and 0xFF2222 or 'RED'
local COLOR_CYAN = is_halo and 0x00D9FF or 'BLUE'
local COLOR_GREY = is_halo and 0x888888 or 'GREY'

local current_mode = "STANDBY" -- "STANDBY", "ITEM_VIEW", "ALERT"
local current_item = {
    name = "Frame Smart Glasses",
    sku = "FRM-BLK-001",
    qty = 12,
    min = 5,
    location = "Aisle 1, Bay A1",
    status = "IN_STOCK"
}

function clear_display()
    if is_halo then
        frame.display.clear(COLOR_BG)
    else
        -- Frame clears on show or via blank rects
    end
end

function flush_display()
    frame.display.show()
end

function play_alert_sound(is_critical)
    if is_halo and frame.sound then
        if is_critical then
            -- High pitch double alert beep
            frame.sound(1000, 150)
            frame.sleep(0.08)
            frame.sound(1200, 250)
        else
            -- Confirmation chime
            frame.sound(600, 100)
            frame.sleep(0.05)
            frame.sound(800, 150)
        end
    end
end

-- Render HUD in 256x256 (Halo) format
function render_halo_hud(mode)
    clear_display()
    
    if mode == "ALERT" then
        -- Red header banner
        frame.display.rect(8, 12, 240, 36, COLOR_RED, true)
        frame.display.text("!! INVENTORY ALERT !!", 24, 22, 0x000000)
        
        frame.display.text("SKU: " .. current_item.sku, 20, 60, COLOR_YELLOW)
        frame.display.text(string.sub(current_item.name, 1, 20), 20, 85, COLOR_WHITE)
        
        local status_text = (current_item.qty == 0) and "OUT OF STOCK (0 pcs)" or ("LOW STOCK: " .. current_item.qty .. "/" .. current_item.min)
        frame.display.text(status_text, 20, 115, COLOR_RED)
        
        frame.display.text("Loc: " .. current_item.location, 20, 145, COLOR_CYAN)
        frame.display.text("[Tap] Acknowledge", 35, 185, COLOR_GREY)
        frame.display.text("[Dbl Tap] Order Restock", 20, 210, COLOR_GREY)
        play_alert_sound(true)

    elseif mode == "ITEM_VIEW" then
        -- Cyan header
        frame.display.rect(8, 12, 240, 32, COLOR_CYAN, false)
        frame.display.text("INVENTORY SCAN", 45, 20, COLOR_CYAN)
        
        frame.display.text(current_item.sku, 20, 58, COLOR_YELLOW)
        frame.display.text(string.sub(current_item.name, 1, 20), 20, 82, COLOR_WHITE)
        
        local color = (current_item.qty == 0) and COLOR_RED or ((current_item.qty <= current_item.min) and COLOR_YELLOW or COLOR_GREEN)
        frame.display.text("Qty: " .. current_item.qty .. " (Min: " .. current_item.min .. ")", 20, 110, color)
        frame.display.text("Loc: " .. current_item.location, 20, 138, COLOR_CYAN)
        
        frame.display.text("[Click] +1 Qty", 35, 175, COLOR_WHITE)
        frame.display.text("[Dbl Click] -1 Qty", 35, 200, COLOR_WHITE)
        play_alert_sound(false)

    else
        -- Standby HUD
        frame.display.rect(8, 8, 240, 240, COLOR_GREY, false)
        frame.display.text("INVENTORY HUD", 45, 30, COLOR_CYAN)
        frame.display.text("Ready to scan", 50, 80, COLOR_WHITE)
        frame.display.text("Aim glasses at item", 30, 115, COLOR_GREY)
        frame.display.text("or tap to cycle alerts", 25, 140, COLOR_GREY)
        frame.display.text("Active Alerts: " .. (alerts_count or 0), 40, 180, COLOR_YELLOW)
    end

    flush_display()
end

-- Render HUD in 640x400 (Frame) format
function render_frame_hud(mode)
    if mode == "ALERT" then
        frame.display.text("========================================", 40, 30, {color=COLOR_RED})
        frame.display.text("           [!] INVENTORY ALERT [!]       ", 40, 60, {color=COLOR_RED})
        frame.display.text("========================================", 40, 90, {color=COLOR_RED})
        
        frame.display.text("Item Name : " .. current_item.name, 50, 140, {color=COLOR_WHITE})
        frame.display.text("Item SKU  : " .. current_item.sku, 50, 180, {color=COLOR_YELLOW})
        
        local status_text = (current_item.qty == 0) and "STATUS    : CRITICAL - OUT OF STOCK (0 pcs)" or ("STATUS    : WARNING - LOW STOCK (" .. current_item.qty .. " / Min " .. current_item.min .. ")")
        frame.display.text(status_text, 50, 220, {color=COLOR_RED})
        frame.display.text("Location  : " .. current_item.location, 50, 260, {color=COLOR_CYAN})
        
        frame.display.text("Controls: [Tap once] Acknowledge  |  [Double tap] Request Restock", 50, 330, {color=COLOR_GREY})

    elseif mode == "ITEM_VIEW" then
        frame.display.text("=== INVENTORY DETAILS ===", 50, 30, {color=COLOR_CYAN})
        frame.display.text("Name    : " .. current_item.name, 50, 80, {color=COLOR_WHITE})
        frame.display.text("SKU     : " .. current_item.sku, 50, 120, {color=COLOR_YELLOW})
        
        local color = (current_item.qty == 0) and COLOR_RED or ((current_item.qty <= current_item.min) and COLOR_YELLOW or COLOR_GREEN)
        frame.display.text("Stock   : " .. current_item.qty .. " units (Min Threshold: " .. current_item.min .. ")", 50, 160, {color=color})
        frame.display.text("Location: " .. current_item.location, 50, 200, {color=COLOR_CYAN})
        
        frame.display.text("Quick Actions:", 50, 260, {color=COLOR_WHITE})
        frame.display.text("[Single Tap] Check In (+1)   [Double Tap] Check Out (-1)", 50, 300, {color=COLOR_GREY})

    else
        frame.display.text("BRILLIANT INVENTORY HUD", 160, 50, {color=COLOR_CYAN})
        frame.display.text("System Online - Bluetooth Connected", 130, 120, {color=COLOR_WHITE})
        frame.display.text("Awaiting barcode scan or alert trigger...", 110, 170, {color=COLOR_GREY})
        frame.display.text("Active Alerts: " .. (alerts_count or 0), 220, 240, {color=COLOR_YELLOW})
    end

    flush_display()
end

function render_hud()
    if is_halo then
        render_halo_hud(current_mode)
    else
        render_frame_hud(current_mode)
    end
end

-- Bind physical triggers
if frame.imu and frame.imu.tap_callback then
    frame.imu.tap_callback(function()
        print("HUD_EVENT:TAP")
    end)
end

if is_halo and frame.button then
    frame.button.single = function()
        print("HUD_EVENT:BUTTON_SINGLE")
    end
    frame.button.double = function()
        print("HUD_EVENT:BUTTON_DOUBLE")
    end
end

-- Initial render
render_hud()
print("HUD_READY")

