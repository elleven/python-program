#!/bin/bash

#STEP  1
#执行获取当前在使用的镜像白名单
./exposeServcieVersion
mv /tmp/version   ./WhiteListFile.txt


# STEP 2
# 清空仓库缓存

redis-cli -h 172.28.1.103 -p 6379 | redis-cli FLUSHALL


# STEP 3
# 执行清理镜像脚本

python registry-gc.py

# STEP 4
#仓库机器上执行layers物理删除（gc）

docker exec -it 5440d7ea65de  registry garbage-collect   /etc/docker/registry/config.yml
 
