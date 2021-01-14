#!/bin/bash
set -ue

yandexDir=$PWD
source ${yandexDir}/rc_env
source ${yandexDir}/rc_local

SCRIPT_DIR=$(dirname "${BASH_SOURCE[0]}")
set +u
if [ ! -d ${SCRIPT_DIR}/.venv ]; then
  virtualenv -p python3 ${SCRIPT_DIR}/.venv
  source ${SCRIPT_DIR}/.venv/bin/activate
  pip3 install -r ${SCRIPT_DIR}/requirements.txt
  deactivate
fi

OLDPWD=$(pwd)
cd ${SCRIPT_DIR}
source .venv/bin/activate
cd $OLDPWD

set -u
sim=${1}



export rpsSchedule="const(50,30s)line(50,250,5m)"

envsubst < ${TEMPLATE_FILE} > ${yandexDir}/shoot.ini

# yandex run
currArtDir=$(yandex-tank -c ${yandexDir}/shoot.ini ${sampleDir}/${sim}.txt | grep ${YANDEX_ARTIFACT_BASE_DIR} | tail -1 | awk '{print $NF}')

# copy test results
simDir=${yandexDir}/$sim
mkdir $simDir
mv ${currArtDir}/phout_*.log $simDir/phout.log

# cleanup
rm -r ${currArtDir}

# metrics collection
startDate=$(head -1 $simDir/phout.log | awk '{printf("%d",$1)}')
endDate=$(tail -1 $simDir/phout.log | awk '{printf("%d",$1)}')

for load in shortterm midterm longterm ; do
  collectPrometheusData -E $PROMETHEUS_ENDPOINT -u $PROMETHEUS_USER -p $PROMETHEUS_PASS -m collectd_load_${load} -i ${instanceId} -s $startDate -e $endDate -S 1s > ${simDir}/load_$load.csv
done
collectPrometheusData -E $PROMETHEUS_ENDPOINT -u $PROMETHEUS_USER -p $PROMETHEUS_PASS -m collectd_memory -i ${instanceId} -s $startDate -e $endDate -S 1s -o memory > ${simDir}/memory.csv
collectPrometheusData -E $PROMETHEUS_ENDPOINT -u $PROMETHEUS_USER -p $PROMETHEUS_PASS -m collectd_cpu_percent -i ${instanceId} -s $startDate -e $endDate -S 1s -o cpu > ${simDir}/cpu.csv


# first analysis and output
cd $simDir
yandex-stats -t 11000 phout.log > stats.txt

cd ${yandexDir}

tar -czf ${sim}.tar.gz  $(basename ${simDir})
rm -r ${simDir}


