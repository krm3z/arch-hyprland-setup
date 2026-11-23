# 0 · Vue d'ensemble

## Le point de départ

- Machine : **HP OmniBook X**, Intel Core Ultra 7 258V (Lunar Lake), SSD NVMe de 1 To, écran 1,25× (`eDP-1`).
- Windows 11 déjà installé, Arch Linux installé à côté (GRUB, `systemd-boot` non utilisé).
- Utilisateur : `kerem`, francophone, clavier AZERTY, fuseau `Europe/Paris`.
- Demande : un bureau **minimaliste mais soigné**, aux **raccourcis Windows**, **tout en français**, et qui change
  de look d'un coup selon un fond d'écran.
- Mode de travail : Claude Code fait tout d'un bloc sans demander de confirmation, puis rend un résumé
  (fait / échoué / raccourcis / « puis-je redémarrer ? »). Seules les commandes `sudo` demandent le mot de passe,
  que l'utilisateur tape lui-même (Claude lui donne les commandes exactes).

## Chronologie

| Date | Session | Ce qui a été fait |
|---|---|---|
| 2026-11-19 | Installation | Arch installé à côté de Windows (partitions, GRUB, locale, réseau). Voir [chap. 1](01-systeme-base.md). |
| **2026-11-21** | Bureau de base | Hyprland (config Lua), waybar, wofi/rofi, mako, swayosd, hyprlock/hypridle, scripts français dans `~/.local/bin`, fiche `Raccourcis.md`, GRUB personnalisé + thème minimal, partition `PARTAGE` exFAT, puis le **système de 11 thèmes** (`generer.py`, `theme`, awww, eww, Ghostty). |
| **2026-11-22** | Applications | Applis AUR/dépôts (Claude Desktop, VS Code, Chrome, Discord, Teams, LibreOffice FR, DBeaver, PostgreSQL, JupyterLab…), 11 applis web Chrome, grille `Windows+A` (nwg-drawer), 6 icônes eww, trousseau pour Electron/Chrome, Timeshift, ufw. |
| **2026-11-23** | Wi-Fi, boutique, ménage | Profil Wi-Fi d'entreprise 802.1X, `nm-applet` comme agent de secrets, Flatpak + boutique *Logiciels* (Flathub), couleur d'accent GNOME qui suit le thème, nettoyage de la grille (35 applis gardées), Chrome devient le navigateur par défaut, `maj-auto`. |

## Architecture

```
                            ┌────────────────────────────┐
  ~/Pictures/Fonds-ecran/ ─►│  generer.py + couleurs.py  │◄── ~/.config/themes/NN-nom/theme.toml
                            └─────────────┬──────────────┘
                                          │ écrit
                                          ▼
                         ~/.config/themes/NN-nom/gen/*   (hypr.lua, waybar.css, …)
                                          ▲
              lien symbolique « actuel » ─┘            ┌─► Hyprland (theme.lua, hyprlock.conf)
                          ▲                            ├─► waybar (style.css)      ├─► mako (config)
   script `theme` ────────┴── recharge les programmes ─┼─► wofi / rofi / nwg-drawer ├─► eww (horloge, icônes)
   (Super+F1, W…)                                      └─► Ghostty / kitty          └─► awww (fond animé)
```

Principes de conception (les décisions qui ont guidé tout le reste) :

1. **Une seule source de vérité par thème** (`theme.toml`) ; tout le reste est généré, jamais édité à la main.
2. **Liens symboliques** plutôt que copies : changer de thème = déplacer un lien + recharger.
3. **Forme fixe, couleurs variables** : la structure de la barre ne change pas d'un thème à l'autre
   (`installer-barre.py` l'écrit une fois) ; seules les couleurs, la transparence et le flou changent.
4. **La documentation se génère** : chaque raccourci Hyprland porte une description `"Catégorie | Action"`,
   `raccourcis-generer` fabrique `~/Bureau/Raccourcis.md` à chaque rechargement de la config.
5. **Lisibilité garantie** : le générateur mesure le contraste et ajuste luminosité/opacité de la barre (rapport
   dans `~/.config/themes/verification.txt`).
6. **Tout en français**, y compris les noms de commandes (`theme regenerer`, `capture zone`, `grille-applis`).
7. **Réversible** : sauvegardes `*.avant-*` avant chaque modification majeure, instantanés Timeshift.

## Où vit quoi

| Chose | Emplacement |
|---|---|
| Config Hyprland | `~/.config/hypr/hyprland.lua`, `theme.lua` (lien), `hypridle.conf`, `hyprlock.conf` (lien) |
| Thèmes + générateur | `~/.config/themes/` (`NN-nom/theme.toml`, `bin/`, `actuel`) |
| Commandes maison | `~/.local/bin/` (liens vers `themes/bin/` + scripts propres) |
| Fiche des raccourcis | `~/Bureau/Raccourcis.md` (générée) |
| Applis web | `~/.local/share/applications/appli-web-<id>.desktop` |
| GRUB | `/etc/grub.d/06_arch`, `07_windows`, `08_uefi`, `/boot/grub/themes/minimal` |
| Mises à jour auto | `/usr/local/bin/maj-auto`, `/etc/systemd/system/maj-auto.{service,timer}` |
| Sauvegardes | Timeshift (rsync, racine uniquement), `/etc/cron.d/timeshift-hourly` |
