#!/bin/bash
#apt-get install zsh -y
#wait
#chsh -s /usr/bin/zsh
wget https://github.com/robbyrussell/oh-my-zsh/raw/master/tools/install.sh -O - | bash
wait
cp ~/.oh-my-zsh/templates/zshrc.zsh-template ~/.zshrc
git clone git://github.com/joelthelion/autojump.git
wait
cd autojump
python ./install.py
cd -

