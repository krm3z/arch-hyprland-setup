# 🤖 Prompt pour tout refaire depuis un Arch nu

## Avant de coller le prompt

1. Arch installé **au minimum** : base, `linux`, `linux-firmware`, GRUB, NetworkManager, `sudo`, un utilisateur dans `wheel`,
   connexion réseau OK, `git` + `base-devel` installés. (Partitions et GRUB : voir [`docs/01`](../docs/01-systeme-base.md) et [`docs/02`](../docs/02-grub-dualboot.md).)
2. Connecté en console (`tty1`) avec cet utilisateur.
3. Installer Claude Code (`npm i -g @anthropic-ai/claude-code`, ou la méthode officielle) et se placer dans le dépôt :
   ```bash
   git clone https://github.com/<toi>/arch-hyprland-setup.git ~/arch-hyprland-setup && cd ~/arch-hyprland-setup && claude
   ```
4. Mettre les images de fond dans `~/Pictures/Fonds-ecran/` (noms dans [`docs/04-themes.md`](../docs/04-themes.md)) — optionnel au début :
   Claude peut générer des dégradés de remplacement.
5. Copier le bloc ci-dessous **en entier**.

---

## Le prompt (à copier-coller)

```text
Tu es Claude Code, sur un Arch Linux tout juste installé (base + GRUB + NetworkManager + sudo). Le dépôt cloné dans le dossier
courant (~/arch-hyprland-setup) contient la documentation complète (docs/), les VRAIES configs (config/), les listes de paquets
(packages/) et des scripts (scripts/) d'un bureau que je veux reproduire à l'identique : Hyprland 0.57 (config en Lua) avec un
système de 11 thèmes générés à partir de fonds d'écran, des raccourcis façon Windows, tout en français.

OBJECTIF
Reproduis ce bureau sur CETTE machine, de bout en bout, en autonomie.

COMMENCE PAR LIRE (dans cet ordre) : README.md, docs/00-vue-ensemble.md, docs/10-pieges-et-lecons.md, puis chaque chapitre au
moment où tu en as besoin. La doc est la référence ; les fichiers de config/ sont la vérité. En cas de doute, ne devine pas :
relis le fichier.

RÈGLES DE TRAVAIL
1. Parle-moi en français. Travaille d'une traite, sans me demander de confirmation pour ce qui est réversible. Pose UNE seule fois,
   au tout début, les questions que tu ne peux pas détecter toi-même (nom d'utilisateur à utiliser, ai-je des fonds d'écran,
   dois-je configurer un Wi-Fi d'entreprise, y a-t-il un Windows à côté), puis ne me dérange plus.
2. Détecte le matériel (lscpu, lspci, lsblk, hyprctl monitors, ls /sys/class/power_supply) et ADAPTE : écran (nom, résolution, échelle ;
   constantes ECRAN/ECHELLE de generer.py et hl.monitor), pilote vidéo (LIBVA_DRIVER_NAME, paquets vulkan/intel-media ou mesa/nvidia),
   disposition clavier (AZERTY par défaut), UUID des partitions, nom d'utilisateur (remplace /home/kerem), présence de Windows
   (sinon pas de 07_windows ni de « Redémarrer sous Windows »), présence d'une batterie.
3. sudo : tu n'as pas mon mot de passe. Regroupe les commandes root en blocs courts et donne-les-moi à lancer avec « ! sudo … » ;
   ne crée JAMAIS de règle NOPASSWD générale. Seule exception autorisée : sudoers.d pour « grub-reboot windows11 ».
   Pour l'AUR, construis avec makepkg dans ~/.cache/aur-build/ (hors sudo) puis donne-moi « sudo pacman -U … ».
   Toujours « sudo pacman -Syu --needed … », jamais -Sy seul.
4. Avant de modifier un fichier qui existe déjà, copie-le en <fichier>.avant-<sujet>-AAAA-MM-JJ.
5. Aucun secret dans un fichier : pas de mot de passe Wi-Fi (trousseau gnome-keyring via nm-applet), pas de jeton.
6. N'automatise pas mon écran (pas d'ouverture de fenêtres/grille pendant les tests). Vérifie par fichiers et IPC : hyprctl configerrors,
   hyprctl binds -j, eww ping, makoctl list, theme actuel, journalctl, systemctl --failed. Pour une capture : grim (résolution physique !).
7. Glyphes Nerd Font : ne les tape pas, génère-les par code (python chr(0xF…)) et contrôle avec od.
8. Si une étape échoue, diagnostique (logs), corrige, et continue ; note-la pour le résumé. Ne boucle pas plus de 3 essais sur la même erreur.
9. Ne pas redémarrer sans me le dire. Ne pas toucher aux partitions Windows ni formater quoi que ce soit.

PLAN (coche chaque phase avec une todo list ; vérifie la phase avant de passer à la suivante)

PHASE 1 — Système de base (docs/01) : locale fr_FR.UTF-8, KEYMAP=fr, fuseau Europe/Paris, hostname, pacman.conf (Color,
  ParallelDownloads=5, NoExtract des scripts GRUB), reflector (config/system/reflector.conf), services (NetworkManager, bluetooth,
  power-profiles-daemon, thermald, cronie, fstrim.timer, paccache.timer, reflector.timer), groupes video/input/lp pour l'utilisateur,
  partition de partage exFAT si elle existe (fstab nofail), Windows exclu de toute écriture.
PHASE 2 — Paquets (packages/README.md) : pacman.txt avec --needed, yay-bin depuis l'AUR, puis aur.txt (eww, ccusage, claude-desktop,
  google-chrome, visual-studio-code-bin, github-desktop-bin, teams-for-linux, polices AUR, curseur Bibata). Pas de packagekit.
PHASE 3 — Configs utilisateur : lance scripts/install-config.sh après l'avoir relu et adapté (nom d'utilisateur, écran). Il copie config/home,
  recrée les liens des commandes dans ~/.local/bin, génère les 11 thèmes (images de ~/Pictures/Fonds-ecran ; sans images, crée des
  dégradés de remplacement aux bons noms plutôt que d'échouer), active le thème de départ et écrit la barre.
PHASE 4 — GRUB (docs/02) : installe 06_arch/07_windows/08_uefi adaptés à CETTE machine (UUID !), désactive les scripts d'origine,
  copie le thème minimal, régénère grub.cfg. Donne-moi les commandes root, vérifie /boot/grub/grub.cfg (entrées Arch, Windows, UEFI),
  ne touche pas à l'entrée EFI de Windows.
PHASE 5 — Session : ~/.bash_profile lance « exec start-hyprland » sur tty1 ; vérifie hyprland.lua (hyprctl configerrors vide), les
  raccourcis, hypridle/hyprlock, nm-applet, swayosd, cliphist, XDG_DATA_DIRS flatpak.
PHASE 6 — Applications (docs/06) : flags trousseau (chrome-flags.conf, claude-desktop-flags.conf, ~/.vscode/argv.json), PostgreSQL
  (initdb fr_FR.UTF-8, rôle + base du nom de l'utilisateur), les 11 applis web avec scripts/creer-appli-web.sh, masquage des entrées
  techniques de la grille Windows+A (copies NoDisplay=true + X-Grille-Masquee=true), Chrome par défaut (xdg-settings / mimeapps).
PHASE 7 — Réseau/Flatpak (docs/07) : flathub système, gnome-software, bloc XDG_DATA_DIRS ; Wi-Fi d'entreprise 802.1X SEULEMENT si je
  l'ai demandé (je te donnerai l'identifiant ; le mot de passe est saisi par moi dans la fenêtre de nm-applet).
PHASE 8 — Maintenance (docs/08) : Timeshift rsync (quotidien ×5, exclusions /home, /mnt, /root), cron horaire, ufw (deny in), maj-auto.service/.timer.
PHASE 9 — Vérification finale (checklist ci-dessous) puis résumé.

CHECKLIST DE VÉRIFICATION (tout doit être OK ou signalé)
- hyprctl configerrors : vide ; hyprctl binds -j : toutes les descriptions présentes ; ~/Bureau/Raccourcis.md généré.
- theme liste : 11 thèmes ; theme suivant puis precedent fonctionnent ; ~/.config/themes/verification.txt : contrastes OK.
- Liens : ~/.config/hypr/theme.lua, hyprlock.conf, waybar/style.css, wofi/style.css, rofi/couleurs.rasi, mako/config, eww/eww.yuck+scss,
  kitty/theme.conf, nwg-drawer/drawer.css pointent vers ~/.config/themes/actuel/gen/…
- Processus : waybar, mako, awww-daemon, eww, swayosd-server, hypridle, nm-applet, cliphist (wl-paste) en cours.
- systemctl --failed vide ; ufw status active ; timeshift --list ; systemctl list-timers (maj-auto, reflector, paccache).
- Applis web : 11 .desktop appli-web-* ; grille : 35 applis environ ; gnome-software sans PackageKit.
- grub.cfg : entrées « Arch Linux », « Windows 11 » (si présent), « Paramètres UEFI ».

LIVRABLE FINAL (en français, court) : ce qui est fait ✅, ce qui a échoué ❌ (avec la cause), ce que je dois faire moi-même
(commandes sudo restantes, mot de passe Wi-Fi, images de fond), les raccourcis principaux (Windows+F1 thème, Windows+A grille,
Windows+F2 fiche, Windows+L verrouiller…), et si je peux redémarrer sans risque.

COMMENCE maintenant par la lecture du README puis pose tes questions initiales (une seule fois).
```

---

## Variante courte (si le dépôt est déjà déployé et que tu veux seulement un nouveau thème)

```text
Lis docs/04-themes.md. Crée un 12ᵉ thème « <nom> » avec l'image ~/Pictures/Fonds-ecran/<fichier> : theme.toml (couleurs indicatives,
polices, barre, bordures, animations, positions de l'horloge et des icônes dans la zone calme de l'image), puis
« theme regenerer <nom> », vérifie verification.txt (contrastes) et applique-le avec « theme appliquer <nom> ». Ne touche à rien d'autre.
```
