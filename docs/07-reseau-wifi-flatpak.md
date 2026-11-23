# 7 · Réseau, Wi-Fi d'entreprise, Flatpak

Session du 23 novembre 2026.

## NetworkManager

Réseau géré par NetworkManager (`nmcli`). Profils : `WiFi@YNOV` (priorité 10), un partage de connexion iPhone et la box
domestique (priorité 0). Le Wi-Fi invité `VDI@YNOV` (WPA2-PSK) n'est pas configuré.

## Profil 802.1X `WiFi@YNOV`

WPA2 Entreprise, **PEAP + MSCHAPv2** (a fonctionné du premier coup). Création (remplace les valeurs entre `<>`) :

```bash
nmcli connection add type wifi con-name "WiFi@YNOV" ssid "WiFi@YNOV" \
  wifi-sec.key-mgmt wpa-eap 802-1x.eap peap 802-1x.phase2-auth mschapv2 \
  802-1x.identity "<prenom.nom@ecole.fr>" \
  802-1x.password-flags 1 \
  802-1x.system-ca-certs yes 802-1x.domain-suffix-match "radius.auvence.co" \
  connection.autoconnect-priority 10
```

- `password-flags 1` = **« agent-owned »** : le mot de passe n'est écrit dans aucun fichier ; il vit dans le **trousseau GNOME**
  et est fourni par un agent de secrets.
- Validation du certificat RADIUS : CA du système (chaîne Gandi → DigiCert Global Root G2) **+** `domain-suffix-match`
  `radius.auvence.co` (épinglage du serveur, évite l'attaque par faux point d'accès). Vérifier le sujet dans
  `journalctl -u wpa_supplicant | grep EAP-PEER-CERT`.
- **`nm-applet` est lancé au démarrage de Hyprland** (`hl.exec_cmd("nm-applet")`) : c'est lui l'agent de secrets, sans lui l'autoconnexion n'a
  pas le mot de passe. Pas d'icône visible (la barre n'a pas de *tray*). Réglages `gsettings` : notifications « connecté »
  et « réseaux disponibles » désactivées.
- Première connexion : la fenêtre du mot de passe apparaît (nm-applet), à saisir **une fois** ; cocher « enregistrer ».
- Reconnexion : `nmcli connection up "WiFi@YNOV"`.

## Flatpak et boutique Logiciels

- `flatpak`, `gnome-software` (sans PackageKit : voulu — la boutique ne gère que Flatpak ; Arch se met à jour par `yay`),
  dépôt `flathub` en **système** : `flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo`.
- Règle polkit de Flatpak : les membres de `wheel` installent/désinstallent sans mot de passe.
- La session part de `tty1` avec `XDG_DATA_DIRS` **vide** ⇒ les `.desktop` Flatpak n'apparaissent pas. Correctif dans `hyprland.lua` :
  un bloc `do … end` qui ajoute `/var/lib/flatpak/exports/share` et `~/.local/share/flatpak/exports/share` devant `XDG_DATA_DIRS`.
- Test fait puis annulé : `org.gnome.Calculator` installé, lancé, désinstallé, `flatpak uninstall --unused`.
- Piège : un index de dépôt pacman périmé a donné un **404 sur `hwloc`** et pacman a abandonné en silence côté utilisateur →
  toujours `sudo pacman -Syu --needed …` (jamais `-S` seul, jamais de `-Sy` partiel).
