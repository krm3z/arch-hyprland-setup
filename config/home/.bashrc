#
# ~/.bashrc
#

# If not running interactively, don't do anything
[[ $- != *i* ]] && return

alias ls='ls --color=auto'
alias grep='grep --color=auto'
PS1='[\u@\h \W]\$ '
export PATH="$HOME/.local/bin:$PATH"

# --- Confort ---
[ -r /usr/share/bash-completion/bash_completion ] && . /usr/share/bash-completion/bash_completion
eval "$(fzf --bash 2>/dev/null)"
HISTSIZE=10000; HISTFILESIZE=20000; HISTCONTROL=ignoreboth:erasedups; shopt -s histappend
PS1='\[\e[38;2;229;72;77m\]\u\[\e[0m\]@\h \[\e[38;2;139;139;144m\]\w\[\e[0m\] \$ '
alias ll='ls -lh --group-directories-first --color=auto'
alias la='ls -lAh --group-directories-first --color=auto'
alias maj='yay -Syu'
alias nettoyer='yay -Yc && sudo paccache -rk2'
