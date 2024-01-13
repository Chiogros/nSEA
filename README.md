# nSEA

> (not) Safe Exam Addon

## What

nSEA is a script which provides the assets needed to access [Safe Exam
Browser (SEB)](https://safeexambrowser.org) exams without SEB, through
an usual browser.

Features:

- [x] Unencrypted Config Key (password-less exam)
- [ ] Encrypted Config Key
- [ ] Browser Exam Key

## Why

SEB isn't available for GNU/Linux. Linux students, whenever an exam is
taken, have to connect through school computers with Windows.

## How

It should work on any Python v3+.

``` sh
$ python ./nsea.py [-h] config_file
```

`config_file` is the XML `config.seb` file you can get from the exam
webpage, the one telling you that you are not using SEB.

Once the script finished, you will get a HTTP key-value header:

    X-SafeExamBrowser-ConfigKeyHash: 6eb3652038ec372a2f2ec0c374e2cbf2c924e9b5d5aade177e7cef57f0598580

This header has to be sent to every SEB-needed webpage to keep access to
the exam. The simpliest way is to install a browser addon, able to
append HTTP headers during your navigation. One of them is
[SimpleModifyHeaders](https://github.com/didierfred/SimpleModifyHeaders)
for
[Firefox](https://addons.mozilla.org/firefox/addon/simple-modify-header/)
and
[Chrome](https://chrome.google.com/webstore/detail/simple-modify-headers/gjgiipmpldkpbdfjkgofildhapegmmic).

## Nota bene

This project is for educational purposes and must not be used without
permission. I do not guarantee that it will work and I am not
responsible for anything that may happen to you.
