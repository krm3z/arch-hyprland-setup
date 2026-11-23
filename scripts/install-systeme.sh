#!/bin/bash
# À lancer en root (sudo) APRÈS install-config.sh : GRUB personnalisé, mises à jour auto, sauvegardes, pare-feu.
# Lis chaque étape avant de lancer : elle touche au démarrage de la machine.
set -euo pipefail
[ "$EUID" -eq 0 ] || { echo "Lance : sudo $0"; exit 1; }
DEPOT="$(cd "$(dirname "$0")/.." && pwd)"
S="$DEPOT/config/system"
UTIL="${SUDO_USER:-kerem}"

echo "→ pacman.conf : NoExtract des scripts GRUB d'origine (on les remplace par les nôtres)"
grep -q '^NoExtract' /etc/pacman.conf || sed -i '/^\[options\]/a NoExtract   = etc/grub.d/10_linux etc/grub.d/20_linux_xen etc/grub.d/30_os-prober etc/grub.d/30_uefi-firmware etc/grub.d/31_efi_bootnext' /etc/pacman.conf
sed -i 's/^#\?Color/Color/; s/^#\?ParallelDownloads.*/ParallelDownloads = 5/' /etc/pacman.conf

echo "→ GRUB : entrées Arch / Windows / UEFI + thème minimal"
install -m755 "$S/06_arch" "$S/07_windows" "$S/08_uefi" /etc/grub.d/
chmod -x /etc/grub.d/10_linux /etc/grub.d/20_linux_xen /etc/grub.d/30_os-prober /etc/grub.d/30_uefi-firmware /etc/grub.d/31_efi_bootnext 2>/dev/null || true
cp -r "$S/grub-theme-minimal" /boot/grub/themes/minimal
echo "   Vérifie UUID de la partition EFI dans 07_windows (6C10-AD7F chez l'auteur) AVANT de continuer."
echo "   Compare $S/grub.default avec /etc/default/grub puis : grub-mkconfig -o /boot/grub/grub.cfg"

echo "→ Wi-Fi/miroirs/mises à jour automatiques"
install -m644 "$S/reflector.conf" /etc/xdg/reflector/reflector.conf
install -m755 "$S/maj-auto" /usr/local/bin/maj-auto
sed -i "s/^USER_NOM=.*/USER_NOM=$UTIL/" /usr/local/bin/maj-auto
install -m644 "$S/maj-auto.service" "$S/maj-auto.timer" /etc/systemd/system/
install -m644 "$S/timeshift-hourly" /etc/cron.d/timeshift-hourly
systemctl daemon-reload
systemctl enable --now maj-auto.timer reflector.timer paccache.timer fstrim.timer cronie.service ufw.service \
  NetworkManager.service bluetooth.service power-profiles-daemon.service thermald.service fwupd-refresh.timer
ufw default deny incoming; ufw default allow outgoing; ufw --force enable

echo "→ « Redémarrer sous Windows » (menu-alimentation) : règle sudo précise, sans mot de passe"
echo "$UTIL ALL=(root) NOPASSWD: /usr/bin/grub-reboot windows11" > /etc/sudoers.d/10-grub-reboot-windows
chmod 440 /etc/sudoers.d/10-grub-reboot-windows; visudo -c

echo "Timeshift : crée la config avec  sudo timeshift --create  ou adapte $S/timeshift.json (UUID de ta racine) vers /etc/timeshift/timeshift.json"
