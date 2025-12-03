FROM python:3.10-slim

# 設置工作目錄
WORKDIR /app

# 安裝中文支援
RUN apt-get update && apt-get install -y \
    locales \
    && rm -rf /var/lib/apt/lists/*

# 生成中文 locale
RUN sed -i '/^#.* zh_TW.UTF-8 /s/^#//' /etc/locale.gen && \
    sed -i '/^#.* zh_CN.UTF-8 /s/^#//' /etc/locale.gen && \
    locale-gen

# 設置環境變量支援中文
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV PYTHONIOENCODING=utf-8

# 複製 requirements.txt
COPY requirements.txt .

# 安裝python需要套件
RUN pip install --no-cache-dir -r requirements.txt

# 複製專案檔案
COPY . .

# port
EXPOSE 5000

# 設置環境變量
ENV PYTHONPATH=/app

# 執行程式
CMD ["sh", "-c", "python3 src/util/threshold_monitor.py & python3 src/util/modbus_collector.py & python3 app.py"]
# CMD ["python", "app.py"]