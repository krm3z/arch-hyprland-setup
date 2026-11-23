# 2 · GRUB et double démarrage

Objectif : un menu **minimal et fiable** — *Arch Linux*, *Windows 11*, *Paramètres UEFI* — qui ne casse pas à chaque mise à jour.

## Principe : scripts maison, scripts d'origine désactivés

`grub-mkconfig` assemble `/etc/grub.d/*` dans l'ordre. Les scripts d'origine (`10_linux`, `30_os-prober`…) produisent des
entrées en double (initramfs de secours, détection Windows approximative). Ils sont remplacés par trois scripts maison :

| Script | Rôle |
|---|---|
| [`06_arch`](../config/system/06_arch) | une entrée par noyau trouvé dans `/boot/vmlinuz-*` (Arch, Arch LTS…), microcode inclus, `root=UUID=` calculé |
| [`07_windows`](../config/system/07_windows) | chaîne vers `\EFI\Microsoft\Boot\bootmgfw.efi` sur la partition EFI (`search --fs-uuid`), id de menu **`windows11`** |
| [`08_uefi`](../config/system/08_uefi) | entrée « Paramètres UEFI » (`fwsetup`) seulement si le firmware le supporte |

Les originaux sont neutralisés de deux façons (ceinture + bretelles) :
`chmod -x /etc/grub.d/{10_linux,20_linux_xen,30_os-prober,30_uefi-firmware,31_efi_bootnext}` **et** `NoExtract` dans
`pacman.conf` (sinon une mise à jour de `grub` remet les droits d'exécution).

## `/etc/default/grub`

```
GRUB_DEFAULT="arch-linux"                    GRUB_DISABLE_RECOVERY=true
GRUB_TIMEOUT=30   GRUB_TIMEOUT_STYLE=menu    GRUB_DISABLE_OS_PROBER=true
GRUB_CMDLINE_LINUX_DEFAULT="loglevel=3 quiet"
GRUB_GFXMODE=1920x1200x32,auto   GRUB_GFXPAYLOAD_LINUX=keep
GRUB_PRELOAD_MODULES="part_gpt part_msdos"   GRUB_TERMINAL_INPUT=console
GRUB_THEME="/boot/grub/themes/minimal/theme.txt"
```
(fichier complet : [`config/system/grub.default`](../config/system/grub.default))

## Thème « minimal »

[`config/system/grub-theme-minimal/`](../config/system/grub-theme-minimal/) : fond uni `background.png`, polices `.pf2`
(Inter 16/26, mono 18) générées avec `grub-mkfont`, sélection en 9 patches (`select_*.png`), icônes `arch/windows/efi`.
À copier dans `/boot/grub/themes/minimal/`.

## Appliquer

```bash
sudo grub-mkconfig -o /boot/grub/grub.cfg
# EFI : grub-install --target=x86_64-efi --efi-directory=/efi --bootloader-id=GRUB   (une seule fois)
```

## « Redémarrer sous Windows » (une seule fois, sans toucher à GRUB)

Dans le menu d'alimentation (`Super+X`) :

```bash
sudo -n /usr/bin/grub-reboot windows11 && systemctl reboot
```
`grub-reboot` écrit `next_entry` dans `grubenv` : GRUB démarre Windows **une fois**, puis revient à Arch. Pour que
`sudo -n` marche sans mot de passe, une règle `sudoers` étroite autorise **uniquement** cette commande
(`/etc/sudoers.d/10-grub-reboot-windows`, créée par `scripts/install-systeme.sh`).

## Pièges

- Si Windows est mis à jour et réécrit l'entrée EFI, relancer `efibootmgr` / `grub-install`.
- L'UUID de la partition EFI (`search --fs-uuid`) est **en dur** dans `07_windows` : à adapter.
- `GRUB_DISABLE_OS_PROBER=true` : on ne veut plus de détection automatique (elle ajouterait des doublons).
