# Auto newsletter

This is a small Python script that polls the Github API for issues and pull
requests of a public repository and sends an email to a defined address (e.g. a
mailing list) every two weeks. It relies on some configuration files and some
configuration in the file itself.

Usage:

There are no command-line parameters, instead the script relies on some configuration files and some hard-coded configurations inside the script. If you want to adapt the script to a different project follow the following steps:

- Adopt the text and sender and receiver address inside the script for your application. Functions to read through and adapt:
  - `get_headers()`
  - `get_pull_request_headers()`
  - `get_issue_headers()`
  - `get_footers()`
  - `send_mail()`
  - the repository queried in the call to `requests.get()`

- Make sure to replace the `me` and `you` addresses inside `send_mail` for testing purposes.

- Periodically run (e.g. through cron). You can control the frequency of emails by adjusting the check for `report_timespan`.

Configuration files in this folder:

- `last_send`: Date and time of last sent email. Example format: '2021-02-25 17:00:01'. This file is automatically updated by the script if it sends an email.

- `number`: The number of the newsletter. Example format: '1'. Will be automatically incremented every time an email is sent.

- `token`: A github access token as explained here: https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token. The token does not need any special permissions, but the API requires a token. Do not check this into the repository!

- `pw`: A password to the email server to allow sending out the emails. Do not check this into the repository!
