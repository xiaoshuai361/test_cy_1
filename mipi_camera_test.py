import cv2
import time
import os

def main():
    # 树莓派 5 专用方案：TCP 网络流
    # 由于 Pi 5 的 libcamera 架构限制，Docker 内直接读取 /dev/video 极其复杂且不稳定
    # 我们采用 "宿主机推流 -> Docker 读取" 的模式，这是目前 Pi 5 最稳健的方案
    
    # 我们假设 Docker 运行时会使用 --net=host 模式
    stream_url = "tcp://127.0.0.1:8888"
    
    print("="*50)
    print("树莓派 5 MIPI 摄像头 Docker 解决方案")
    print("="*50)
    print(f"正在尝试连接视频流: {stream_url}")
    print("\n[重要] 请务必在树莓派宿主机(非Docker内)的新终端运行以下命令启动推流:")
    print("rpicam-vid -t 0 --inline --listen -o tcp://0.0.0.0:8888 --width 640 --height 480")
    print("\n等待连接中 (请先在宿主机运行上述命令)...")

    cap = cv2.VideoCapture(stream_url)
    
    # 尝试连接几次
    connected = False
    for i in range(5):
        if cap.isOpened():
            connected = True
            break
        print(f"尝试连接... {i+1}/5")
        time.sleep(2)
        cap.open(stream_url)

    if not connected:
        print("\n错误: 无法连接到视频流。")
        print("请检查：")
        print("1. 是否在宿主机运行了 rpicam-vid 命令")
        print("2. Docker 运行命令是否添加了 --net=host 参数")
        return

    print("连接成功！正在读取帧...")
    
    # 读取一帧
    ret, frame = cap.read()

    if ret:
        output_file = 'capture.jpg'
        cv2.imwrite(output_file, frame)
        print(f"成功! 图片已保存为 {output_file}")
    else:
        print("错误: 无法读取帧")

    # 释放资源
    cap.release()

if __name__ == "__main__":
    main()
