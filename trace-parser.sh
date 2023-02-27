#!/usr/bin/env bash

rm *.log
rm *.csv

dir=$1
if ! [ -d "${dir}" ]; then exit 66; fi
matcherScript="$(dirname "$0")/trace-matcher.py"
if ! [ -f "${matcherScript}" ]; then exit 67; fi

echo "Glue all trace files into one and sort it."
traceLogSorted="$(date +'%Y-%m-%dT%H:%M:%S' | tr ':' '+' ).log"
cat $dir/*/*.trace | sort > "${traceLogSorted}"

echo "Grep publish packets and line numbers."
publishAllFile="publish-${traceLogSorted}"
grep -n 'Received PUBLISH message' ${traceLogSorted} > "${publishAllFile}"

echo "Grep puback packets and line number."
pubAckAllFile="puback-${traceLogSorted}"
grep -n 'Sent PUBACK message' "${traceLogSorted}" > "${pubAckAllFile}"

echo "Parse publish packets into csv."
parsedPublishAllFile="parsed-${publishAllFile}.csv"
echo "pubLine,pubTime,clientId,packetId,topic,qos,duplicate,expiry" > "${parsedPublishAllFile}"
rg '^(\d+):(.{23}) - \[([^\[^\]]+)\] - Received PUBLISH message \(packet identifier: (\d+), topic: ([^,]+), QoS: (\d+), retain: false, duplicate delivery: ([a-z]+), message expiry interval: (\d+)\)' \
  -r '$1,"$2","$3",$4,"$5",$6,"$7",$8' "${publishAllFile}" >> "${parsedPublishAllFile}"

echo "Parse puback packets into csv."
parsedPubAckAllFile="parsed-${pubAckAllFile}.csv"
echo "ackLine,ackTime,clientId,packetId,reasonCode" > "${parsedPubAckAllFile}"
rg '(\d+):(.{23}) - \[([^\[^\]]+)\] - Sent PUBACK message \(packet identifier: (\d+), reason code: (\d+)\).*$' \
  -r '$1,"$2","$3",$4,$5' "${pubAckAllFile}" >> "${parsedPubAckAllFile}"

echo "Start the Python matcher"
logFile="output.log"
python3 "${matcherScript}" "${parsedPublishAllFile}" "${parsedPubAckAllFile}" 2>&1 | tee "${logFile}"