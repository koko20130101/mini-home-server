#!/bin/bash

# 设置Daphne的路径，根据你的安装位置修改
DAPHNE_PATH=$(which daphne)
 
# 设置你的ASGI应用程序的模块路径，例如 'myproject.asgi:application'
ASGI_APP='MiniHome.asgi:application'
 
# 设置Daphne服务器的IP地址和端口，例如 '0.0.0.0:8000'
HOST='127.0.0.1'
PORT='8002'
 
case "$1" in
    start)
        echo "Starting Daphne server..."
        nohup $DAPHNE_PATH -b $HOST -p $PORT $ASGI_APP > /dev/null 2>&1 &
        ;;
    stop)
        echo "Stopping Daphne server..."
        # 对于大多数情况，直接杀死所有daphne进程可能不是最佳选择，因为它可能不会优雅地关闭连接。
        # 更安全的做法是编写一个更复杂的停止脚本，例如使用pgrep和pkill。
        pkill -f "daphne -b $HOST -p $PORT $ASGI_APP"
        ;;
    restart)
        echo "Restarting Daphne server..."
        pkill -f "daphne -b $HOST -p $PORT $ASGI_APP" && sleep 1 && nohup $DAPHNE_PATH -b $HOST -p $PORT $ASGI_APP > /dev/null 2>&1 &
        ;;
    *)
        echo "Usage: $0 {start|stop|restart}"
        exit 1
        ;;
esac