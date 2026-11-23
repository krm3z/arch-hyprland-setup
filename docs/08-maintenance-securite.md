# 8 · Maintenance et sécurité

## Timeshift (instantanés du système)

Mode **rsync** (ext4, pas btrfs) sur la partition racine. Config : [`config/system/timeshift.json`](../config/system/timeshift.json)
(à adapter : `backup_device_uuid`). Planification : **quotidien ×5** (hebdo/mensuel/boot désactivés), plus `/etc/cron.d/timeshift-hourly`
(`0 * * * * root timeshift --check --scripted`, exécuté par `cronie`).
Exclus : `/home/kerem/**`, `/mnt/**`, `/root/**`, `/var/lib/postgres/data/postmaster.pid` — **les données personnelles ne sont PAS dans
les instantanés** (sauvegarde du `/home` = à faire à part, ou via le disque PARTAGE).

## Mises à jour automatiques (`maj-auto`)

[`/usr/local/bin/maj-auto`](../config/system/maj-auto) lancé par `maj-auto.timer` **2 min après chaque démarrage** (`OnBootSec=2min`) :

1. une seule fois par jour (`/var/lib/maj-auto/derniere`), attend le réseau (ping `archlinux.org`, 2 min max), abandonne si pacman est verrouillé ;
2. **instantané Timeshift** « avant maj-auto » ;
3. `pacman -Syu --noconfirm` puis `flatpak update -y` ;
4. notification utilisateur (en passant par `runuser` + bus D-Bus de la session) + signal à waybar ; journal `/var/log/maj-auto.log`.

Les paquets AUR restent à mettre à jour à la main : alias `maj` (= `yay -Syu`), `nettoyer` (= `yay -Yc && sudo paccache -rk2`).

## Pare-feu

`ufw` activé : entrant refusé, sortant autorisé (`LOGLEVEL=low`).

## Miroirs et cache

`reflector.timer` (miroirs rapides) et `paccache.timer` ; `fstrim.timer` pour le SSD ; `fwupd-refresh.timer` pour les firmwares.

## Énergie

`power-profiles-daemon` (profils `power-saver` / `balanced` / `performance`, choix par `Super+I`) + `thermald`. Le profil a été laissé en
« performance » à la fin de la session du 22.

## Sudo : principe de moindre privilège

- L'utilisateur est dans `wheel` (sudo avec mot de passe).
- Pendant les longues sessions Claude, un `sudoers.d/99-…-nopasswd` **temporaire** a été utilisé comme filet de sécurité puis supprimé
  (l'extinction programmée le retirait en dernier recours). **Ne jamais le laisser en place.**
- Une seule règle permanente attendue : `grub-reboot windows11` sans mot de passe (menu « Redémarrer sous Windows », `scripts/install-systeme.sh` la crée).
- Les commandes `sudo` que Claude ne peut pas lancer sont **données telles quelles** à l'utilisateur (`! sudo …` dans le prompt de Claude Code).
