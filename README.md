# nSEA

> (not) Safe Exam Addon

## What

nSEA is a script which provides the assets needed to access [Safe Exam
Browser (SEB)](https://safeexambrowser.org) exams without SEB, through
a standard browser.

Supported levels of security ([help wanted](https://github.com/Chiogros/nSEA/discussions)):
- [x] Unencrypted Config Key (CK)
- [x] Password-encrypted Config Key
- [ ] Public key-encrypted Config Key
- [ ] Server Exam Key
- [ ] Browser Exam Key (BEK)
- [ ] Additional Browser Exam Key (ABEK)
- [ ] App-Signature Key (ASK)

## Why

SEB isn't available for GNU/Linux.

## How

``` sh
$ pip3 install cryptography
$ python3 ./nsea.py [-h] config_file.seb
```

`config.seb` is XML or GZIP file you can get from the exam
webpage, the one telling you that you are not using SEB.

Once the script is finished, you will get a HTTP key-value header:

    X-SafeExamBrowser-ConfigKeyHash: 6eb3652038ec372a2f2ec0c374e2cbf2c924e9b5d5aade177e7cef57f0598580

This header has to be sent to every SEB-needed webpage to keep access to
the exam. The simpliest way is to install a browser addon, able to
append HTTP headers during your navigation. One of them is
[SimpleModifyHeaders](https://github.com/didierfred/SimpleModifyHeaders)
for
[Firefox](https://addons.mozilla.org/firefox/addon/simple-modify-header/)
and
[Chrome](https://chrome.google.com/webstore/detail/simple-modify-headers/gjgiipmpldkpbdfjkgofildhapegmmic).

## Resources

[Developer documentation - Config key](https://safeexambrowser.org/developer/seb-config-key.html)

## Nota bene

This project is for educational purposes (especially about software-protection mechanisms) and must not be used without
permission. I do not guarantee that it will work and I am not responsible for any usage of this tool.

Dear organizations and schools, paying exam supervisors and using paper sheet/pencil are the best, IT non-hackable way to pass an exam.
As you may have noticed, not all security mechanisms are supported. You may upgrade your exams to a greatest level!
