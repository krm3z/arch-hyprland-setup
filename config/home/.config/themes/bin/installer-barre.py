#!/usr/bin/env python3
"""Écrit ~/.config/waybar/config.jsonc (forme fixe de la barre, identique pour tous les thèmes).
Les glyphes Nerd Font sont écrits par leur code pour ne jamais être perdus."""
import json
from pathlib import Path

G = lambda cp: chr(cp)
config = {
    "layer": "top", "position": "top", "height": 34,
    "margin-top": 6, "margin-left": 10, "margin-right": 10, "spacing": 0,
    "modules-left": ["custom/claude", "hyprland/workspaces"],
    "modules-center": ["clock"],
    "modules-right": ["group/systeme", "group/controles", "group/session"],

    "custom/claude": {
        "exec": "claude-usage", "return-type": "json", "interval": 30, "signal": 9,
        "format": "{}", "escape": False, "tooltip": True,
        "on-click": "setsid -f google-chrome-stable https://claude.ai/settings/usage",
        "on-click-right": "pkill -RTMIN+9 waybar",
    },
    "hyprland/workspaces": {
        "format": "{name}",
        "persistent-workspaces": {"*": 5},
        "on-click": "activate", "sort-by-number": True,
        "on-scroll-up": "hyprctl dispatch 'hl.dsp.focus({ workspace = \"e-1\" })'",
        "on-scroll-down": "hyprctl dispatch 'hl.dsp.focus({ workspace = \"e+1\" })'",
    },
    "clock": {
        "format": "{:L%a %d %b  %H:%M}", "format-alt": "{:L%A %d %B %Y  %H:%M:%S}",
        "interval": 1, "locale": "fr_FR.UTF-8",
        "tooltip-format": "<tt><small>{calendar}</small></tt>",
        "calendar": {"mode": "month", "on-scroll": 1,
                     "format": {"months": "<b>{}</b>", "today": "<b><u>{}</u></b>"}},
        "actions": {"on-scroll-up": "shift_down", "on-scroll-down": "shift_up"},
    },

    "group/systeme": {"orientation": "horizontal", "modules": ["cpu", "memory", "temperature"]},
    "group/controles": {"orientation": "horizontal",
                        "modules": ["pulseaudio", "network", "bluetooth", "backlight", "battery"]},
    "group/session": {"orientation": "horizontal", "modules": ["custom/notif", "custom/alim"]},

    "cpu": {"interval": 3, "format": G(0xF0EE0) + " {usage}%", "tooltip-format": "Processeur : {usage} %",
            "on-click": "setsid -f missioncenter"},
    "memory": {"interval": 5, "format": G(0xF035B) + " {percentage}%",
               "tooltip-format": "Mémoire : {used:0.1f} Go / {total:0.1f} Go utilisés",
               "on-click": "setsid -f missioncenter"},
    "temperature": {"hwmon-path-abs": "/sys/devices/platform/coretemp.0/hwmon", "input-filename": "temp1_input",
                    "critical-threshold": 90, "interval": 5,
                    "format": "{icon} {temperatureC}°", "format-icons": [G(0xF10C2), G(0xF050F), G(0xF10C3)],
                    "tooltip-format": "Température du processeur : {temperatureC} °C"},
    "pulseaudio": {
        "format": "{icon} {volume}%", "format-muted": G(0xF075F), "format-bluetooth": G(0xF00B0) + " {volume}%",
        "format-icons": {"headphone": G(0xF02CB), "default": [G(0xF057F), G(0xF0580), G(0xF057E)]},
        "scroll-step": 5, "max-volume": 100, "tooltip-format": "{desc} — {volume} %\nClic : mixeur · clic droit : muet",
        "on-click": "pavucontrol", "on-click-right": "swayosd-client --output-volume mute-toggle",
    },
    "network": {
        "format-wifi": "{icon}", "format-ethernet": G(0xF0200), "format-disconnected": G(0xF092D),
        "format-disabled": G(0xF092D), "format-icons": [G(0xF092F), G(0xF0922), G(0xF0925), G(0xF0928)],
        "tooltip-format-wifi": "{essid} ({signalStrength} %)\n{ipaddr}\nClic : choisir un réseau",
        "tooltip-format-ethernet": "{ifname} — {ipaddr}",
        "tooltip-format-disconnected": "Déconnecté — cliquer pour choisir un réseau",
        "on-click": "wifi-menu", "on-click-right": "nm-connection-editor",
    },
    "bluetooth": {
        "format": G(0xF00AF), "format-disabled": G(0xF00B2), "format-off": G(0xF00B2),
        "format-connected": G(0xF00B1) + " {num_connections}",
        "tooltip-format": "Bluetooth : {status}\nClic : appareils · clic droit : activer/désactiver",
        "tooltip-format-connected": "{device_enumerate}", "tooltip-format-enumerate-connected": "{device_alias}",
        "on-click": "blueman-manager", "on-click-right": "rfkill toggle bluetooth",
    },
    "backlight": {"format": "{icon} {percent}%", "format-icons": [G(0xF00DE), G(0xF00DF), G(0xF00E0)],
                  "on-scroll-up": "swayosd-client --brightness raise",
                  "on-scroll-down": "swayosd-client --brightness lower --min-brightness 1",
                  "tooltip-format": "Luminosité : {percent} % (molette pour régler)"},
    "battery": {
        "interval": 30, "states": {"warning": 20, "critical": 10},
        "format": "{icon} {capacity}%", "format-charging": G(0xF0084) + " {capacity}%",
        "format-plugged": G(0xF06A5) + " {capacity}%",
        "format-icons": [G(0xF007A), G(0xF007C), G(0xF007E), G(0xF0080), G(0xF0079)],
        "tooltip-format": "{timeTo}\n{power:.1f} W", "format-time": "{H} h {M} min",
    },
    "custom/notif": {
        "exec": "notifications etat", "return-type": "json", "interval": 5, "signal": 10,
        "format": "{}", "escape": False,
        "on-click": "notifications historique", "on-click-right": "notifications nepasderanger",
        "on-click-middle": "notifications effacer",
    },
    "custom/alim": {"format": G(0x23FB), "tooltip-format": "Alimentation : verrouiller, veille, redémarrer, éteindre",
                    "on-click": "menu-alimentation"},
}
dest = Path.home() / ".config/waybar/config.jsonc"
dest.write_text("// Waybar — forme fixe (générée par ~/.config/themes/bin/installer-barre.py).\n"
                "// Les couleurs viennent du thème actif : style.css -> ~/.config/themes/actuel/gen/waybar.css\n"
                + json.dumps(config, indent=2, ensure_ascii=False) + "\n")
print("écrit :", dest)
