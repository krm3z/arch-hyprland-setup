-- ════════════════════════════════════════════════════════════════════
--  Hyprland — config de kerem (HP OmniBook X, AZERTY)
--  Bureau à thèmes, raccourcis façon Windows.
--  Fiche des raccourcis : Super + F2  (fichier ~/Bureau/Raccourcis.md)
--  Thèmes : Super + F1 (suivant) · Super + Maj + F1 (précédent)
--
--  Chaque raccourci a une description « Catégorie | Action » : la fiche
--  ~/Bureau/Raccourcis.md est régénérée automatiquement à chaque
--  rechargement de cette config (ou à la main : raccourcis-generer).
--  Après modification : la config se recharge toute seule.
-- ════════════════════════════════════════════════════════════════════

----------------
--  ÉCRAN     --
----------------
hl.monitor({
    output   = "eDP-1",
    mode     = "preferred",
    position = "auto",
    scale    = 1.25,
})
-- Écrans externes (HDMI / USB-C) : à droite, échelle automatique
hl.monitor({
    output   = "",
    mode     = "preferred",
    position = "auto-right",
    scale    = "auto",
})


-------------------
--  PROGRAMMES   --
-------------------
local terminal    = "ghostty"
local fichiers    = "thunar"
local navigateur  = "google-chrome-stable"
local lanceur     = "pkill -x wofi || wofi --show drun"
local gestionTach = "missioncenter"


-------------------------------
--  VARIABLES D'ENVIRONNEMENT --
-------------------------------
hl.env("XCURSOR_THEME", "Bibata-Modern-Classic")
hl.env("XCURSOR_SIZE", "24")
hl.env("HYPRCURSOR_SIZE", "24")
hl.env("TERMINAL", "ghostty")
hl.env("QT_QPA_PLATFORM", "wayland;xcb")
hl.env("QT_QPA_PLATFORMTHEME", "qt6ct")
hl.env("QT_WAYLAND_DISABLE_WINDOWDECORATION", "1")
hl.env("XDG_MENU_PREFIX", "arch-")             -- menus « Ouvrir avec »
hl.env("LIBVA_DRIVER_NAME", "iHD")             -- décodage vidéo matériel Intel
hl.env("ELECTRON_OZONE_PLATFORM_HINT", "auto")  -- applis Electron en Wayland natif
hl.env("_JAVA_AWT_WM_NONREPARENTING", "1")
-- Applis Flatpak (boutique « Logiciels ») visibles dans le lanceur et la grille Windows + A
do
    local maison = os.getenv("HOME") or "/home/kerem"
    local dirs = os.getenv("XDG_DATA_DIRS")
    if not dirs or dirs == "" then dirs = "/usr/local/share:/usr/share" end
    for _, d in ipairs({ "/var/lib/flatpak/exports/share", maison .. "/.local/share/flatpak/exports/share" }) do
        if not (":" .. dirs .. ":"):find(":" .. d .. ":", 1, true) then dirs = d .. ":" .. dirs end
    end
    hl.env("XDG_DATA_DIRS", dirs)
end


-------------------------
--  DÉMARRAGE AUTO     --
-------------------------
hl.on("hyprland.start", function()
    hl.exec_cmd("dbus-update-activation-environment --systemd --all")
    hl.exec_cmd("systemctl --user start hyprpolkitagent")
    -- Agent NetworkManager : garde le mot de passe Wi-Fi Ynov dans le trousseau (pas dans un fichier)
    -- et le fournit pour la reconnexion automatique. Pas d'icône (la barre n'a pas de zone « tray »).
    hl.exec_cmd("nm-applet")
    -- Thème actif (fond d'écran awww, barre waybar, notifications mako, widgets eww)
    hl.exec_cmd("theme demarrage")
    hl.exec_cmd("swayosd-server")
    hl.exec_cmd("hypridle")
    hl.exec_cmd("hyprctl setcursor Bibata-Modern-Classic 24")
    hl.exec_cmd("wl-paste --type text --watch cliphist store")
    hl.exec_cmd("wl-paste --type image --watch cliphist store")
    hl.exec_cmd("wl-clip-persist --clipboard regular")
    hl.exec_cmd("udiskie --automount --notify")
    hl.exec_cmd("alerte-batterie")
    hl.exec_cmd("barre-plein-ecran")
    hl.exec_cmd("raccourcis-generer --silencieux")
end)

-- La fiche des raccourcis suit la config : régénérée à chaque rechargement
hl.on("config.reloaded", function()
    hl.exec_cmd("raccourcis-generer --silencieux")
end)


-------------------------
--  APPARENCE          --
-------------------------
-- Valeurs de base ; le thème actif (~/.config/hypr/theme.lua -> thème choisi)
-- remplace couleurs des bordures, flou, ombres et animations.
hl.config({
    general = {
        gaps_in     = 4,
        gaps_out    = 10,
        border_size = 2,
        col = {
            active_border   = { colors = { "rgba(e5484dff)", "rgba(f76b15ff)" }, angle = 45 },
            inactive_border = "rgba(ffffff14)",
        },
        resize_on_border = true,   -- redimensionner en tirant le bord (comme Windows)
        allow_tearing    = false,
        layout           = "dwindle",
    },

    decoration = {
        rounding       = 12,
        rounding_power = 2,
        active_opacity   = 1.0,
        inactive_opacity = 1.0,
        shadow = {
            enabled      = true,
            range        = 18,
            render_power = 3,
            color        = "rgba(00000066)",
        },
        blur = {
            enabled  = true,
            size     = 6,
            passes   = 3,
            vibrancy = 0.17,
            popups   = true,
        },
    },

    animations = { enabled = true },
})

-- Thème actif : couleurs, flou de la barre, style des animations
local fichierTheme = os.getenv("HOME") .. "/.config/hypr/theme.lua"
local okTheme, errTheme = pcall(dofile, fichierTheme)
if not okTheme then
    -- Secours si le thème est absent : animations par défaut
    hl.curve("easeOutQuint", { type = "bezier", points = { {0.23, 1}, {0.32, 1} } })
    hl.animation({ leaf = "global",     enabled = true, speed = 6, bezier = "easeOutQuint" })
    hl.animation({ leaf = "windowsIn",  enabled = true, speed = 4, bezier = "easeOutQuint", style = "popin 87%" })
    hl.animation({ leaf = "workspaces", enabled = true, speed = 4, bezier = "easeOutQuint", style = "fade" })
    hl.layer_rule({ name = "theme-barre", match = { namespace = "^waybar$" }, blur = true, ignore_alpha = 0.05 })
    print("Thème introuvable : " .. tostring(errTheme))
end

hl.config({
    dwindle = { preserve_split = true },
    master  = { new_status = "master" },
})

hl.config({
    misc = {
        force_default_wallpaper  = 0,
        disable_hyprland_logo    = true,
        disable_splash_rendering = true,
        focus_on_activate        = true,
        close_special_on_empty   = true,
        mouse_move_enables_dpms  = true,
        key_press_enables_dpms   = true,
    },
    cursor    = { sync_gsettings_theme = true, inactive_timeout = 0 },
    ecosystem = { no_update_news = true, no_donation_nag = true },
    layers    = { allow_new_top_layers_over_existing_fullscreen = false },
})


-------------------
--  CLAVIER/SOURIS --
-------------------
hl.config({
    input = {
        kb_layout  = "fr",
        kb_variant = "",
        kb_model   = "",
        kb_options = "",
        kb_rules   = "",
        numlock_by_default = true,
        repeat_rate  = 35,
        repeat_delay = 300,
        follow_mouse = 1,
        sensitivity  = 0,
        touchpad = {
            natural_scroll       = true,  -- défilement « naturel » comme sous Windows
            tap_to_click         = true,  -- toucher = clic
            disable_while_typing = true,
            clickfinger_behavior = true,  -- clic à 2 doigts = clic droit
            scroll_factor        = 0.7,
        },
    },
})

-- Balayage horizontal à 3 doigts = changer de bureau
hl.gesture({ fingers = 3, direction = "horizontal", action = "workspace" })


----------------------
--  RACCOURCIS      --
----------------------
-- Format des descriptions : "Catégorie | Action" (utilisé par la fiche des raccourcis)
local SUPER = "SUPER"
local function d(texte) return { description = texte } end

-- Thèmes ------------------------------------------------------------
hl.bind(SUPER .. " + F1",         hl.dsp.exec_cmd("theme suivant"),   d("Thèmes | Thème suivant"))
hl.bind(SUPER .. " + SHIFT + F1", hl.dsp.exec_cmd("theme precedent"), d("Thèmes | Thème précédent"))
hl.bind(SUPER .. " + W",          hl.dsp.exec_cmd("theme choisir"),   d("Thèmes | Choisir un thème dans la liste"))
hl.bind(SUPER .. " + SHIFT + W",  hl.dsp.exec_cmd("theme hasard"),    d("Thèmes | Thème au hasard"))

-- Aide --------------------------------------------------------------
hl.bind(SUPER .. " + F2", hl.dsp.exec_cmd("raccourcis"), d("Aide | Afficher / fermer la fiche des raccourcis"))
hl.bind(SUPER .. " + H",  hl.dsp.exec_cmd("raccourcis"), d("Aide | Afficher / fermer la fiche des raccourcis"))

-- Applications ------------------------------------------------------
hl.bind("SUPER + SUPER_L", hl.dsp.exec_cmd(lanceur), { release = true, description = "Applications | Menu des applications (comme le menu Démarrer)" })
hl.bind(SUPER .. " + S",      hl.dsp.exec_cmd(lanceur), d("Applications | Rechercher une application"))
hl.bind(SUPER .. " + SPACE",  hl.dsp.exec_cmd(lanceur), d("Applications | Rechercher une application"))
hl.bind(SUPER .. " + R",      hl.dsp.exec_cmd("pkill -x wofi || wofi --show run"), d("Applications | Exécuter une commande"))
hl.bind(SUPER .. " + E",      hl.dsp.exec_cmd(fichiers),   d("Applications | Explorateur de fichiers (Thunar)"))
hl.bind(SUPER .. " + B",      hl.dsp.exec_cmd(navigateur), d("Applications | Navigateur web (Chrome)"))
hl.bind(SUPER .. " + RETURN", hl.dsp.exec_cmd(terminal),   d("Applications | Ouvrir un terminal (Ghostty)"))
hl.bind(SUPER .. " + T",      hl.dsp.exec_cmd(terminal),   d("Applications | Ouvrir un terminal (Ghostty)"))
hl.bind("CTRL + ALT + T",     hl.dsp.exec_cmd(terminal),   d("Applications | Ouvrir un terminal (Ghostty)"))
hl.bind("CTRL + SHIFT + Escape", hl.dsp.exec_cmd(gestionTach), d("Applications | Gestionnaire des tâches"))
hl.bind(SUPER .. " + I",      hl.dsp.exec_cmd("parametres"), d("Applications | Paramètres rapides (Wi-Fi, son, Bluetooth…)"))
hl.bind(SUPER .. " + A",      hl.dsp.exec_cmd("grille-applis"), d("Applications | Toutes les applications (grille avec recherche, comme le menu Démarrer)"))
hl.bind(SUPER .. " + Y",      hl.dsp.exec_cmd("gtk-launch appli-web-ynov"), d("Applications | Extranet Ynov (appli web)"))
hl.bind(SUPER .. " + semicolon",  hl.dsp.exec_cmd("rofi -show emoji"), d("Applications | Émojis"))
hl.bind(SUPER .. " + SHIFT + C",  hl.dsp.exec_cmd("hyprpicker -a"), d("Applications | Pipette à couleurs (copie le code couleur)"))

-- Presse-papiers ----------------------------------------------------
hl.bind(SUPER .. " + V", hl.dsp.exec_cmd("presse-papiers"), d("Presse-papiers | Historique du presse-papiers (choisir puis coller)"))

-- Notifications -----------------------------------------------------
hl.bind(SUPER .. " + N", hl.dsp.exec_cmd("notifications historique"), d("Notifications | Historique des notifications"))
hl.bind(SUPER .. " + SHIFT + N", hl.dsp.exec_cmd("notifications nepasderanger"), d("Notifications | Activer / désactiver « Ne pas déranger »"))
hl.bind(SUPER .. " + Escape", hl.dsp.exec_cmd("makoctl dismiss --all"), d("Notifications | Fermer toutes les notifications"))

-- Captures d'écran (enregistrées dans ~/Pictures/Captures + presse-papiers)
hl.bind(SUPER .. " + SHIFT + S", hl.dsp.exec_cmd("capture zone"),    d("Captures d'écran | Capturer une zone (comme l'Outil Capture)"))
hl.bind("Print",                 hl.dsp.exec_cmd("capture ecran"),   d("Captures d'écran | Capturer tout l'écran"))
hl.bind(SUPER .. " + Print",     hl.dsp.exec_cmd("capture ecran"),   d("Captures d'écran | Capturer tout l'écran"))
hl.bind("ALT + Print",           hl.dsp.exec_cmd("capture fenetre"), d("Captures d'écran | Capturer la fenêtre active"))
hl.bind("CTRL + Print",          hl.dsp.exec_cmd("capture annoter"), d("Captures d'écran | Capturer une zone et l'annoter (flèches, texte…)"))
hl.bind(SUPER .. " + SHIFT + A", hl.dsp.exec_cmd("capture annoter"), d("Captures d'écran | Capturer une zone et l'annoter (flèches, texte…)"))

-- Fenêtres ----------------------------------------------------------
hl.bind("ALT + F4",        hl.dsp.window.close(), d("Fenêtres | Fermer la fenêtre"))
hl.bind(SUPER .. " + Q",   hl.dsp.window.close(), d("Fenêtres | Fermer la fenêtre"))
hl.bind("F11",             hl.dsp.window.fullscreen(), d("Fenêtres | Plein écran"))
hl.bind(SUPER .. " + F",   hl.dsp.window.fullscreen(), d("Fenêtres | Plein écran (remettre / enlever)"))
hl.bind(SUPER .. " + SHIFT + F", hl.dsp.window.float({ action = "toggle" }), d("Fenêtres | Fenêtre flottante ou en mosaïque"))
hl.bind(SUPER .. " + J",   hl.dsp.layout("togglesplit"), d("Fenêtres | Changer le sens du partage (côte à côte / l'une sur l'autre)"))
hl.bind(SUPER .. " + P",   hl.dsp.window.pin(), d("Fenêtres | Épingler au premier plan (fenêtre flottante)"))

-- Alt+Tab : fenêtre suivante (Maj : précédente), passée au premier plan
hl.bind("ALT + TAB", function()
    hl.dispatch(hl.dsp.window.cycle_next())
    hl.dispatch(hl.dsp.window.bring_to_top())
end, d("Fenêtres | Passer à la fenêtre suivante"))
hl.bind("ALT + SHIFT + TAB", function()
    hl.dispatch(hl.dsp.window.cycle_next({ next = false }))
    hl.dispatch(hl.dsp.window.bring_to_top())
end, d("Fenêtres | Revenir à la fenêtre précédente"))
hl.bind(SUPER .. " + TAB", hl.dsp.exec_cmd("pkill -x rofi || rofi -show window"), d("Fenêtres | Liste des fenêtres ouvertes"))

-- Placement des fenêtres --------------------------------------------
-- Super+↑ : agrandir (ou restaurer une fenêtre réduite)
hl.bind(SUPER .. " + UP", function()
    local w = hl.get_active_window()
    if not w then return end
    if w.workspace and w.workspace.special then
        local ws = hl.get_active_workspace()
        hl.dispatch(hl.dsp.window.move({ workspace = ws and ws.id or "e+0" }))
        return
    end
    if (w.fullscreen or 0) == 0 then
        hl.dispatch(hl.dsp.window.fullscreen({ mode = "maximized" }))
    end
end, d("Placement des fenêtres | Agrandir la fenêtre (ou restaurer une fenêtre réduite)"))

-- Super+↓ : restaurer si agrandie, sinon réduire
hl.bind(SUPER .. " + DOWN", function()
    local w = hl.get_active_window()
    if not w then return end
    local fs = w.fullscreen or 0
    if fs == 1 then
        hl.dispatch(hl.dsp.window.fullscreen({ mode = "maximized" }))
    elseif fs == 2 then
        hl.dispatch(hl.dsp.window.fullscreen())
    else
        hl.dispatch(hl.dsp.window.move({ workspace = "special:reduites", follow = false }))
    end
end, d("Placement des fenêtres | Restaurer la fenêtre, puis la réduire"))
hl.bind(SUPER .. " + SHIFT + M", hl.dsp.workspace.toggle_special("reduites"), d("Placement des fenêtres | Afficher les fenêtres réduites"))

-- Super+← / → : ancrer la fenêtre à gauche / à droite
local function ancrer(dir)
    return function()
        local w = hl.get_active_window()
        if not w then return end
        if (w.fullscreen or 0) == 1 then hl.dispatch(hl.dsp.window.fullscreen({ mode = "maximized" })) end
        if w.floating then hl.dispatch(hl.dsp.window.float({ action = "disable" })) end
        hl.dispatch(hl.dsp.window.move({ direction = dir }))
    end
end
hl.bind(SUPER .. " + LEFT",  ancrer("left"),  d("Placement des fenêtres | Ancrer la fenêtre à gauche"))
hl.bind(SUPER .. " + RIGHT", ancrer("right"), d("Placement des fenêtres | Ancrer la fenêtre à droite"))

-- Super+D : afficher le bureau (appuyer à nouveau pour revenir)
local bureauPrecedent = nil
hl.bind(SUPER .. " + D", function()
    local ws = hl.get_active_workspace()
    if ws and ws.windows == 0 and bureauPrecedent then
        hl.dispatch(hl.dsp.focus({ workspace = bureauPrecedent }))
        bureauPrecedent = nil
    else
        bureauPrecedent = ws and ws.id or nil
        hl.dispatch(hl.dsp.focus({ workspace = "empty" }))
    end
end, d("Placement des fenêtres | Afficher le bureau (encore une fois : revenir)"))

-- Bureaux virtuels (comme Windows) ---------------------------------
hl.bind(SUPER .. " + CTRL + D",     hl.dsp.focus({ workspace = "empty" }), d("Bureaux virtuels | Nouveau bureau vide"))
hl.bind(SUPER .. " + SHIFT + LEFT", function()
    hl.dispatch(hl.dsp.window.cycle_next({ next = false }))
    hl.dispatch(hl.dsp.window.bring_to_top())
end, d("Fenêtres | Passer à la fenêtre précédente"))
hl.bind(SUPER .. " + SHIFT + RIGHT", function()
    hl.dispatch(hl.dsp.window.cycle_next())
    hl.dispatch(hl.dsp.window.bring_to_top())
end, d("Fenêtres | Passer à la fenêtre suivante"))
hl.bind(SUPER .. " + SHIFT + UP", function()
    hl.dispatch(hl.dsp.window.cycle_next({ next = false }))
    hl.dispatch(hl.dsp.window.bring_to_top())
end, d("Fenêtres | Passer à la fenêtre précédente (haut)"))
hl.bind(SUPER .. " + SHIFT + DOWN", function()
    hl.dispatch(hl.dsp.window.cycle_next())
    hl.dispatch(hl.dsp.window.bring_to_top())
end, d("Fenêtres | Passer à la fenêtre suivante (bas)"))
hl.bind(SUPER .. " + CTRL + LEFT",  hl.dsp.window.move({ workspace = "r-1" }), d("Bureaux virtuels | Envoyer la fenêtre sur le bureau de gauche"))
hl.bind(SUPER .. " + CTRL + RIGHT", hl.dsp.window.move({ workspace = "r+1" }), d("Bureaux virtuels | Envoyer la fenêtre sur le bureau de droite"))

-- Super + 1…0 (touches & é " ' ( - è _ ç à) : aller au bureau ; + Maj : y envoyer la fenêtre
for i = 1, 10 do
    local code = "code:" .. (9 + i)
    hl.bind(SUPER .. " + " .. code,         hl.dsp.focus({ workspace = i }),       d("Bureaux virtuels | Aller au bureau " .. i))
    hl.bind(SUPER .. " + SHIFT + " .. code, hl.dsp.window.move({ workspace = i }), d("Bureaux virtuels | Envoyer la fenêtre au bureau " .. i))
end

-- Souris
hl.bind(SUPER .. " + mouse_down", hl.dsp.send_shortcut({ mods = "CTRL", key = "minus" }), d("Affichage | Dézoomer dans l'appli (molette)"))
hl.bind(SUPER .. " + mouse_up",   hl.dsp.send_shortcut({ mods = "CTRL", key = "equal" }), d("Affichage | Zoomer dans l'appli (molette)"))
hl.bind(SUPER .. " + mouse:274",  hl.dsp.send_shortcut({ mods = "CTRL", key = "0" }),     d("Affichage | Zoom normal dans l'appli (clic molette)"))
hl.bind(SUPER .. " + mouse:272",  hl.dsp.window.drag(),   { mouse = true, description = "Souris | Déplacer la fenêtre (maintenir et glisser)" })
hl.bind(SUPER .. " + mouse:273",  hl.dsp.window.resize(), { mouse = true, description = "Souris | Redimensionner la fenêtre (maintenir et glisser)" })

-- Volume et luminosité (avec affichage à l'écran) -------------------
hl.bind("XF86AudioRaiseVolume",  hl.dsp.exec_cmd("swayosd-client --output-volume raise --max-volume 100"), { locked = true, repeating = true, description = "Volume et luminosité | Monter le volume" })
hl.bind("XF86AudioLowerVolume",  hl.dsp.exec_cmd("swayosd-client --output-volume lower"),       { locked = true, repeating = true, description = "Volume et luminosité | Baisser le volume" })
hl.bind("XF86AudioMute",         hl.dsp.exec_cmd("swayosd-client --output-volume mute-toggle"), { locked = true, description = "Volume et luminosité | Couper / rétablir le son" })
hl.bind("XF86AudioMicMute",      hl.dsp.exec_cmd("swayosd-client --input-volume mute-toggle"),  { locked = true, description = "Volume et luminosité | Couper / rétablir le micro" })
hl.bind("XF86MonBrightnessUp",   hl.dsp.exec_cmd("swayosd-client --brightness raise"),          { locked = true, repeating = true, description = "Volume et luminosité | Augmenter la luminosité" })
hl.bind("XF86MonBrightnessDown", hl.dsp.exec_cmd("swayosd-client --brightness lower --min-brightness 1"), { locked = true, repeating = true, description = "Volume et luminosité | Baisser la luminosité" })
hl.bind("XF86AudioNext",  hl.dsp.exec_cmd("swayosd-client --playerctl next"),       { locked = true, description = "Volume et luminosité | Musique : piste suivante" })
hl.bind("XF86AudioPrev",  hl.dsp.exec_cmd("swayosd-client --playerctl prev"),       { locked = true, description = "Volume et luminosité | Musique : piste précédente" })
hl.bind("XF86AudioPlay",  hl.dsp.exec_cmd("swayosd-client --playerctl play-pause"), { locked = true, description = "Volume et luminosité | Musique : lecture / pause" })
hl.bind("XF86AudioPause", hl.dsp.exec_cmd("swayosd-client --playerctl play-pause"), { locked = true, description = "Volume et luminosité | Musique : lecture / pause" })
hl.bind("Caps_Lock",      hl.dsp.exec_cmd("sleep 0.1; swayosd-client --caps-lock"), { release = true, non_consuming = true, description = "Système | Afficher l'état du verrouillage des majuscules" })

-- Verrouillage et alimentation --------------------------------------
hl.bind(SUPER .. " + L",         hl.dsp.exec_cmd("pidof hyprlock || hyprlock"), d("Verrouillage et alimentation | Verrouiller l'écran"))
hl.bind("CTRL + ALT + Delete",   hl.dsp.exec_cmd("menu-alimentation"), d("Verrouillage et alimentation | Menu : verrouiller, veille, redémarrer, éteindre…"))
hl.bind(SUPER .. " + X",         hl.dsp.exec_cmd("menu-alimentation"), d("Verrouillage et alimentation | Menu : verrouiller, veille, redémarrer, éteindre…"))

-- Système -----------------------------------------------------------
hl.bind(SUPER .. " + SHIFT + R", hl.dsp.exec_cmd("theme barre"), d("Système | Relancer la barre et les widgets du bureau"))


------------------------------
--  RÈGLES DES FENÊTRES     --
------------------------------
hl.window_rule({
    name  = "ignorer-maximiser",
    match = { class = ".*" },
    suppress_event = "maximize",
})

hl.window_rule({
    name  = "fix-xwayland-drags",
    match = { class = "^$", title = "^$", xwayland = true, float = true, fullscreen = false, pin = false },
    no_focus = true,
})

-- Petites fenêtres d'outils : flottantes et centrées
hl.window_rule({
    name   = "outils-flottants",
    match  = { class = "^(org.pulseaudio.pavucontrol|blueman-manager|nm-connection-editor|system-config-printer|org.gnome.Calculator|nwg-look|qt6ct|io.missioncenter.MissionCenter|org.kde.ark|flottant|fr.kerem.flottant|com.local.help)$" },
    float  = true,
    center = true,
})
hl.window_rule({
    name  = "taille-outils",
    match = { class = "^(org.pulseaudio.pavucontrol|blueman-manager|nm-connection-editor|flottant|fr.kerem.flottant|io.missioncenter.MissionCenter)$" },
    size  = { 960, 640 },
})
hl.window_rule({
    name  = "taille-calculatrice",
    match = { class = "^(org.gnome.Calculator)$" },
    size  = { 380, 560 },
})

-- Fiche des raccourcis (Super+F2) : jolie fenêtre flottante centrée
hl.window_rule({
    name   = "fiche-raccourcis",
    match  = { class = "^(fr.kerem.raccourcis)$" },
    float  = true,
    center = true,
    size   = { 1000, 800 },
})

-- Thunar : boîtes de dialogue flottantes
hl.window_rule({
    name   = "thunar-dialogues",
    match  = { class = "^(thunar)$", title = "^(Progression de l'opération de fichier|File Operation Progress|Confirmer.*|Renommer.*|Propriétés.*)$" },
    float  = true,
    center = true,
})

-- Firefox : image dans l'image flottante et épinglée
hl.window_rule({
    name  = "firefox-pip",
    match = { title = "^(Incrustation vidéo|Picture-in-Picture)$" },
    float = true,
    pin   = true,
    size  = { 640, 360 },
    move  = "monitor_w-660 monitor_h-380",
})

-- Annotation de capture
hl.window_rule({
    name   = "satty",
    match  = { class = "^(com.gabm.satty)$" },
    float  = true,
    center = true,
})

-- Flou derrière le lanceur, les menus, les notifications et l'OSD
-- (le flou de la barre et des icônes du bureau dépend du thème : theme.lua)
hl.layer_rule({
    name  = "flou-couches",
    match = { namespace = "^(wofi|rofi|notifications|swayosd|nwg-drawer)$" },
    blur  = true,
    ignore_alpha = 0.2,
})
hl.layer_rule({
    name  = "selection-sans-anim",
    match = { namespace = "^(selection|hyprpicker)$" },
    no_anim = true,
})
