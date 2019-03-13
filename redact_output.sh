#!/usr/bin/env sh

sed -e '/CREDENTIALS/ c\<CREDENTIALS REDACTED>' <&0
