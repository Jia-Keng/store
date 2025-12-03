-- 設定資料庫編碼
SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;
SET character_set_client = utf8mb4;
SET character_set_connection = utf8mb4;
SET character_set_results = utf8mb4;

CREATE DATABASE IF NOT EXISTS env_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE env_db;

CREATE TABLE IF NOT EXISTS `kmu_ems_data` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    `溫度01` FLOAT,
    `濕度01` FLOAT,
    `溫度02` FLOAT,
    `濕度02` FLOAT,
    `門禁` FLOAT,
    `UPS電壓` FLOAT,
    `UPS電流` FLOAT,
    INDEX(timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- users 資料表
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 插入測試資料
INSERT INTO `kmu_ems_data` (timestamp, `溫度01`, `濕度01`, `溫度02`, `濕度02`, `門禁`, `UPS電壓`, `UPS電流`) VALUES
(NOW(), 22.91, 67.27, 23.27, 66.25, FALSE, 250.00, 0.0);

-- 溫度: 22.91°C (正常)
-- 濕度: 67.27% (正常)
-- 電壓: 300.9V  超過250V閾值
-- 電流: 0.0A (正常)
-- 門禁: 1  觸發人員進出