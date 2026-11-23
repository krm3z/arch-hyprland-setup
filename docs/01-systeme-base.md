# 1 · Système de base

État final de la machine (relevé sur la machine réelle ; les UUID sont à remplacer par les tiens).

## Disque (NVMe 953,9 Go)

| Partition | Taille | Type | Montage | Rôle |
|---|---|---|---|---|
| `nvme0n1p1` | 260 Mo | FAT32 | `/efi` | partition EFI **partagée avec Windows** (label SYSTEM) |
| `nvme0n1p2` | 16 Mo | — | | MSR Windows |
| `nvme0n1p3` | 582,7 Go | NTFS | | Windows 11 |
| `nvme0n1p4` | 100 Go | exFAT | `/mnt/partage` | **PARTAGE** : données lisibles/écrivables des deux systèmes |
| `nvme0n1p5` | 907 Mo | NTFS | | récupération Windows |
| `nvme0n1p6` | 1 Go | ext4 | `/boot` | noyau, initramfs, GRUB |
| `nvme0n1p7` | 8 Go | swap | | swap |
| `nvme0n1p8` | 100 Go | ext4 | `/` | racine Arch |
| `nvme0n1p9` | 161 Go | ext4 | `/home` | données utilisateur |

`/boot` séparé en ext4 (et non sur l'EFI) : GRUB lit ext4 nativement, les noyaux ne grossissent pas la petite EFI de Windows.

### `/etc/fstab`

```fstab
UUID=<racine>   /            ext4   rw,relatime   0 1
UUID=<boot>     /boot        ext4   rw,relatime   0 2
UUID=<efi>      /efi         vfat   rw,relatime,fmask=0022,dmask=0022,codepage=437,iocharset=ascii,shortname=mixed,utf8,errors=remount-ro  0 2
UUID=<home>     /home        ext4   rw,relatime   0 2
UUID=<swap>     none         swap   defaults      0 0
UUID=<partage>  /mnt/partage exfat  rw,noatime,uid=1000,gid=1000,fmask=0133,dmask=0022,iocharset=utf8,nofail,x-systemd.device-timeout=10s  0 0
```

`nofail` + `x-systemd.device-timeout=10s` : un disque PARTAGE absent ne bloque jamais le démarrage. Lien de commodité :
`~/PARTAGE → /mnt/partage`.

## Paramètres régionaux

```
/etc/hostname     arch
/etc/locale.conf  LANG=fr_FR.UTF-8        (locale.gen : fr_FR.UTF-8 UTF-8)
/etc/vconsole.conf KEYMAP=fr
/etc/localtime    → /usr/share/zoneinfo/Europe/Paris
```
Clavier sous Hyprland : `kb_layout = "fr"` ; chiffres du haut = `&é"'(-è_çà`, donc les raccourcis `Super + 1…0` utilisent les
**keycodes** (`code:10`…`code:19`), pas les symboles (voir [chap. 3](03-hyprland.md)).

## Noyau et initramfs

`/etc/mkinitcpio.conf` : `HOOKS=(base systemd autodetect microcode modconf kms keyboard sd-vconsole block filesystems fsck)`
(initramfs basé systemd + keymap console). Microcode : `intel-ucode`. Paquets : `linux linux-firmware sof-firmware`
(audio Lunar Lake), `intel-media-driver` + `vulkan-intel` (GPU Intel Xe ; `LIBVA_DRIVER_NAME=iHD`), `thermald`.

## pacman

`/etc/pacman.conf` : `Color`, `ParallelDownloads = 5`, `CheckSpace`, et
```
NoExtract = etc/grub.d/10_linux etc/grub.d/20_linux_xen etc/grub.d/30_os-prober etc/grub.d/30_uefi-firmware etc/grub.d/31_efi_bootnext
```
→ les scripts GRUB d'origine ne sont **jamais réinstallés** par une mise à jour de `grub` (voir [chap. 2](02-grub-dualboot.md)).

Miroirs : `reflector` (`/etc/xdg/reflector/reflector.conf`) — HTTPS, France/Allemagne/Belgique/Suisse, 12 h, 20 derniers,
8 plus rapides ; `reflector.timer` actif. `paccache.timer` nettoie le cache.

## Services système activés

`NetworkManager`, `bluetooth`, `power-profiles-daemon`, `thermald`, `cronie`, `ufw`, `postgresql`, `avahi-daemon`,
`systemd-timesyncd`, `cups.socket`, `fstrim.timer`, `fwupd-refresh.timer`, `reflector.timer`, `paccache.timer`,
`maj-auto.timer` (maison), `lm_sensors`.

Services **utilisateur** : `pipewire`, `pipewire-pulse`, `wireplumber`, `xdg-user-dirs`, `gnome-keyring-daemon.socket`,
`p11-kit-server.socket`.

Groupes de `kerem` : `wheel` (sudo), `video` (luminosité), `input`, `lp` (imprimantes).

## Ouverture de session

Pas de gestionnaire de connexion. Connexion texte sur `tty1`, puis `~/.bash_profile` :

```bash
[[ -f ~/.bashrc ]] && . ~/.bashrc
if [ -z "$WAYLAND_DISPLAY" ] && [ -z "$DISPLAY" ] && [ "${XDG_VTNR:-0}" -eq 1 ] && command -v start-hyprland >/dev/null; then
    exec start-hyprland
fi
```
`~/.bashrc` : `PATH` + `~/.local/bin`, `fzf --bash`, historique 10 000 lignes sans doublons, invite colorée,
alias `maj='yay -Syu'` et `nettoyer='yay -Yc && sudo paccache -rk2'`.

> ⚠️ Conséquence : la session ne passe pas par PAM/systemd-logind « graphique » classique, donc `XDG_DATA_DIRS` est vide —
> la config Hyprland le reconstruit (voir [chap. 7](07-reseau-wifi-flatpak.md)). Le trousseau GNOME est déverrouillé
> par PAM au login.
