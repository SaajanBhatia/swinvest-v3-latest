-- MySQL dump 10.13  Distrib 8.0.23, for Linux (x86_64)
--
-- Host: 172.31.2.42    Database: swinvest
-- ------------------------------------------------------
-- Server version	8.0.23

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `accounts`
--

DROP TABLE IF EXISTS `accounts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `accounts` (
  `uid` int NOT NULL AUTO_INCREMENT,
  `username` varchar(300) DEFAULT NULL,
  `firstName` varchar(450) DEFAULT NULL,
  `lastName` varchar(450) DEFAULT NULL,
  `password` varchar(700) DEFAULT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts`
--

LOCK TABLES `accounts` WRITE;
/*!40000 ALTER TABLE `accounts` DISABLE KEYS */;
INSERT INTO `accounts` VALUES (1,'SAAJAN@SSBHATIA.CO.UK','Saajan','Bhatia','$5$rounds=535000$8WtUfBrxhXYNxQkM$ric/X7NdBdTB.gQNzWldQQ1Er5E3F/hvX3fLM77LqR/'),(2,'SMAIGEN@GMAIL.COM','Mr Smaigen','Bossman','$5$rounds=535000$X9N7q7Xq5tjop95j$lvjz6kVSopJcMspVR2MB7RtxRQgPJ7eslfOOi1SSl73'),(3,'TEACHER@SWINVEST.CO.UK','Teacher','Account','$5$rounds=535000$mwKDLSBfk1CHw6Ui$QFw.YhEw.i.T2GxdzLE/l7Xa4MLyk9lZereEQgxXLaB'),(4,'TEST@SWINVEST.CO.UK','John','Smith','$5$rounds=535000$DqeXI3Vi99An2pQM$J5IKcSPwIEkosTWqt3uZvp5WQY.Jtp64AY71Ea0hDyC');
/*!40000 ALTER TABLE `accounts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `preferences`
--

DROP TABLE IF EXISTS `preferences`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `preferences` (
  `pid` int NOT NULL,
  `one` varchar(50) DEFAULT NULL,
  `two` varchar(50) DEFAULT NULL,
  `three` varchar(50) DEFAULT NULL,
  `four` varchar(50) DEFAULT NULL,
  `five` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`pid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `preferences`
--

LOCK TABLES `preferences` WRITE;
/*!40000 ALTER TABLE `preferences` DISABLE KEYS */;
INSERT INTO `preferences` VALUES (1,'{\"Ticker\": \"GOOG\", \"Priority\": 1}','{\"Ticker\": \"GOOGL\", \"Priority\": 2}','{\"Ticker\": \"AMZN\", \"Priority\": 2}','{\"Ticker\": \"TWTR\", \"Priority\": 3}','{\"Ticker\": \"FB\", \"Priority\": 3}'),(2,'{\"Ticker\": \"GOOGL\", \"Priority\": 1}','NONE','NONE','NONE','NONE'),(3,'{\"Ticker\": \"GME\", \"Priority\": 1}','NONE','NONE','NONE','NONE'),(4,'NONE','NONE','NONE','NONE','NONE');
/*!40000 ALTER TABLE `preferences` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2021-02-19 17:54:30
