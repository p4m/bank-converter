# Bank Converter

A personal converter program to consume a csv-file from the Rabobank, to convert it to some FreeAgent accepts for uploading a bank statement.

## Installatie

1. Download source code to local computer
1. Unzip
1. Move the complete unzipped folder to $HOME directory
1. Rename folder name bank-converter-main to BankConverter
1. Click on the install_bankconverter.sh
1. Drag for your convenience folders IN and OUT to your Favorites in Finder

## Handy commands

``` sh

chmod +x ~/BankConverter/install_bankconverter.sh

nano ~/Library/LaunchAgents/nl.user.bankconverter.plist

launchctl load ~/Library/LaunchAgents/nl.user.bankconverter.plist

launchctl unload ~/Library/LaunchAgents/nl.user.bankconverter.plist

launchctl start nl.user.bankconverter
launchctl stop nl.user.bankconverter

ps aux | grep BankConverter

tail -f ~/BankConverter/log.txt
```
