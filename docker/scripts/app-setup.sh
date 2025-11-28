#!/usr/bin/env bash

set -e

USERNAME=${1:-"dev"}
USER_UID=${2:-"1000"}
USER_GID=${3:-"1000"}

export DEBIAN_FRONTEND=noninteractive

# Install sudo
apt-get update
apt-get -y install --no-install-recommends nginx openjdk-25-jre tmux sudo 2>&1
apt-get autoremove -y

# Create or update a non-root user to match UID/GID.
group_name="${USERNAME}"
if id -u ${USERNAME} > /dev/null 2>&1; then
  # User exists, update if needed
  if [ "$USER_GID" != "$(id -g $USERNAME)" ]; then
    group_name="$(id -gn $USERNAME)"
    groupmod --gid $USER_GID ${group_name}
    usermod --gid $USER_GID $USERNAME
  fi
  if [ "$USER_UID" != "$(id -u $USERNAME)" ]; then
    usermod --uid $USER_UID $USERNAME
  fi
else
  # Create user
  groupadd --force --gid $USER_GID $USERNAME
  useradd -s /bin/bash --uid $USER_UID --gid $USERNAME -m $USERNAME || true
fi

# Add add sudo support for non-root user
echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME
chmod 0440 /etc/sudoers.d/$USERNAME

# Restore user .bashrc defaults from skeleton file if it doesn't exist or is empty
if [ ! -f "/home/${USERNAME}/.bashrc" ] || [ ! -s "/home/${USERNAME}/.bashrc" ] ; then
  cp  /etc/skel/.bashrc "/home/${USERNAME}/.bashrc"
fi

# Restore user .profile defaults from skeleton file if it doesn't exist or is empty
if  [ ! -f "/home/${USERNAME}/.profile" ] || [ ! -s "/home/${USERNAME}/.profile" ] ; then
  cp  /etc/skel/.profile "/home/${USERNAME}/.profile"
fi

# Codespaces bash and OMZ themes - partly inspired by https://github.com/ohmyzsh/ohmyzsh/blob/master/themes/robbyrussell.zsh-theme
codespaces_bash="$(cat \
<<'EOF'

# Codespaces bash prompt theme
__bash_prompt() {
    local userpart='`export XIT=$? \
        && echo -n "\[\033[0;32m\]\u " \
        && [ "$XIT" -ne "0" ] && echo -n "\[\033[1;31m\]➜" || echo -n "\[\033[0m\]➜"`'
    local lightblue='\[\033[1;34m\]'
    local removecolor='\[\033[0m\]'
    PS1="${userpart} ${lightblue}\w${removecolor}\$ "
    unset -f __bash_prompt
}
__bash_prompt

EOF
)"

codespaces_zsh="$(cat \
<<'EOF'
# Codespaces zsh prompt theme
__zsh_prompt() {
    PROMPT="%{$fg[green]%}%n %(?:%{$reset_color%}➜ :%{$fg_bold[red]%}➜ )" # User/exit code arrow
    PROMPT+='%{$fg_bold[blue]%}%(5~|%-1~/…/%3~|%4~)%{$reset_color%} ' # cwd
    PROMPT+='%{$fg[white]%}$ %{$reset_color%}'
    unset -f __zsh_prompt
}
ZSH_THEME_GIT_PROMPT_PREFIX="%{$fg_bold[cyan]%}(%{$fg_bold[red]%}"
ZSH_THEME_GIT_PROMPT_SUFFIX="%{$reset_color%} "
ZSH_THEME_GIT_PROMPT_DIRTY=" %{$fg_bold[yellow]%}✗%{$fg_bold[cyan]%})"
ZSH_THEME_GIT_PROMPT_CLEAN="%{$fg_bold[cyan]%})"
__zsh_prompt

EOF
)"

# Add custom bash prompt
echo "${codespaces_bash}" >> "/home/${USERNAME}/.bashrc"
echo 'export PROMPT_DIRTRIM=4' >> "/home/${USERNAME}/.bashrc"
echo "${codespaces_bash}" >> "/root/.bashrc"
echo 'export PROMPT_DIRTRIM=4' >> "/root/.bashrc"
chown ${USERNAME}:${group_name} "/home/${USERNAME}/.bashrc"

# Install and configure zsh and Oh My Zsh!
# Adapted, simplified inline Oh My Zsh! install steps that adds, defaults to a codespaces theme.
# See https://github.com/ohmyzsh/ohmyzsh/blob/master/tools/install.sh for official script.
oh_my_install_dir="/home/${USERNAME}/.oh-my-zsh"
if [ ! -d "${oh_my_install_dir}" ]; then
  template_path="${oh_my_install_dir}/templates/zshrc.zsh-template"
  user_rc_file="/home/${USERNAME}/.zshrc"
  umask g-w,o-w
  mkdir -p ${oh_my_install_dir}
  git clone --depth=1 \
    -c core.eol=lf \
    -c core.autocrlf=false \
    -c fsck.zeroPaddedFilemode=ignore \
    -c fetch.fsck.zeroPaddedFilemode=ignore \
    -c receive.fsck.zeroPaddedFilemode=ignore \
    "https://github.com/ohmyzsh/ohmyzsh" "${oh_my_install_dir}" 2>&1
  echo -e "$(cat "${template_path}")\nDISABLE_AUTO_UPDATE=true\nDISABLE_UPDATE_PROMPT=true" > ${user_rc_file}
  sed -i -e 's/ZSH_THEME=.*/ZSH_THEME="codespaces"/g' ${user_rc_file}

  mkdir -p ${oh_my_install_dir}/custom/themes
  echo "${codespaces_zsh}" > "${oh_my_install_dir}/custom/themes/codespaces.zsh-theme"
  # Shrink git while still enabling updates
  cd "${oh_my_install_dir}"
  git repack -a -d -f --depth=1 --window=1
  # Copy to non-root user
  cp -rf "${user_rc_file}" "${oh_my_install_dir}" /root
  chown -R ${USERNAME}:${group_name} "/home/${USERNAME}"
fi
