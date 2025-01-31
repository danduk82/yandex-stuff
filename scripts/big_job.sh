#!/bin/bash

for layer in $(cat layer_list.txt); do
  for projection in $(cat projection_list.txt); do
    for zoom in $(cat zoomlevels_list.txt); do 
      for service in wms wmts wmts_preview ; do
        if [ $service = "wms" ] ; then 
          export port=8000
        else
          export port=80
        fi
        ./launch-yandex.sh ${layer}_${service}_${projection}${zoom}
      done
    done
  done
done
