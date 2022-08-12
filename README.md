# WordSmash
*"Your WordPress site's best friend"* - Nobody.

[Telegram](https://t.me/the_archivists_domain) | [Discord](https://discord.gg/9X99f5hZAs)

## Features
- Automatically enumerates WordPress usernames
- Scrapes email addresses
- Support for dynamic, site-specific values in passwords
- Checks email account credentials for performing password reset attack
- Multithreded

## Installation
Requires python 3.9 or later.

Install with pip:
```
pip install wordsmash
```
Install from GitHub:
```
pip install git+https://github.com/TheArchivist01/wordsmash.git
```

## Options
`--wordlist`: List of sites to attempt accessing \
`--site-list`: List of sites to attempt accessing \
`--dynamic-wordlist`: Enable dynamic placeholder values in wordlist \
`--persist`: Continue trying to find additional logins for a site after login success \
`--threads`: Maximum number of sites to check in parallel

## Dynamic Wordlist?
The dynamic wordlist feature allows you to use placeholder values in the wordlist.
Currently a password can contain {username} or {domain}.

Example: Logging into examplesite.com as "admin"
```
{username}123       -> admin123
{domain}pass        -> examplesitepass
{username}@{domain} -> admin@examplesite
```

##  More from The Archivist 01
[Telegram](https://t.me/the_archivists_domain)
[Discord](https://discord.gg/9X99f5hZAs)

## Additional credits
@ph03n1x69 for helping with the wordpress login test.

## Disclaimer
WordSmasher is intended to be used for educational and research purposes. \
The Archivist and other contributors are not responsible for damages caused by the use of this tool.

See the [LICENSE](./LICENCE) file for more details.
