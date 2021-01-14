[tank]
;plugin_svgreport=yandextank.plugins.SvgReport
artifacts_base_dir = ${YANDEX_ARTIFACT_BASE_DIR}
plugin_monitoring=
plugin_telegraf=

[phantom]

; space before ; !!!!
address=${instanceId} ;
port=${port} ;target's port
rps_schedule=${rpsSchedule}

header_http = 1.1
headers = [Host: service-proxywms.prod.bgdi.ch]
          [User-Agent: Tank]
          [Referer: http://dans-ta-g.bgdi.ch]
          [Connection: close]

;timeout = 35s
;writelog = all

[autostop]
; stop the test if too many errors (optional)
autostop = http(503,50%,180)
           http(110,50%,10)
           net(101,25%,10)

