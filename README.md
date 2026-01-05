# Bank Converter

A personal converter program to consume a csv-file from the Rabobank, to convert it to some FreeAgent accepts for uploading a bank statement.

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
