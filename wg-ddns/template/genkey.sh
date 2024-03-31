#!/bin/bash
# date 2023-06-15 19:46:00
# author calllivecn <calllivecn@outlook.com>



genkey=$(wg genkey)

pubkey=$(echo "$genkey" |wg pubkey)


echo "私钥：${genkey}"
echo "公钥：${pubkey}"

