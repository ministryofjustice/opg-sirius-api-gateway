#!/usr/bin/env sh

# sed -e "s/CREDENTIALS/<REDACTED>/g" <&0
sed -e '/CREDENTIALS/ c\<CREDENTIALS REDACTED>' <&0
