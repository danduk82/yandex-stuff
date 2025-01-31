# Utilities for yandex-tank

## Disclaimer

The code in this repository is intended solely for benchmarking backend infrastructure. It is provided "as is" without any warranties
or guarantees of any kind. Use at your own risk. Improper usage may negatively impact your infrastructure. The authors are not
responsible for any damage, downtime, or unintended consequences resulting from its use.

## Usage

This repository contains a few utilities that I developped mostly for comfort when using [yandex-tank](https://yandextank.readthedocs.io) to benchmark some backend.

Here is a useful shell function to start within a container with yandex-tank 

```shell
function tank(){
  docker run --rm -v $(pwd):/var/loadtest -u $(id -u):$(id -g) --net host -it --entrypoint /bin/bash yandex/yandex-tank
}
```

And here is a function to run the stats container:

```shell
function stats(){
  docker run --rm -v $(pwd):/workdir -u $(id -u):$(id -g) --net host -it --entrypoint /bin/bash danduk82/yandex-stats
}
```

