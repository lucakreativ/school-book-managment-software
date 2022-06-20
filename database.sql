-- MySQL dump 10.13  Distrib 8.0.29, for Linux (x86_64)
--
-- Host: localhost    Database: create_test
-- ------------------------------------------------------
-- Server version	8.0.29-0ubuntu0.22.04.2

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
-- Table structure for table `addedstudent`
--

DROP TABLE IF EXISTS `addedstudent`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `addedstudent` (
  `ID` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `Stufe` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Klasse` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Vorname` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Nachname` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Religion` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Fremdsp1` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Fremdsp2` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Fremdsp3` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `addedstudent`
--

LOCK TABLES `addedstudent` WRITE;
/*!40000 ALTER TABLE `addedstudent` DISABLE KEYS */;
/*!40000 ALTER TABLE `addedstudent` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ausgeliehen`
--

DROP TABLE IF EXISTS `ausgeliehen`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ausgeliehen` (
  `ID` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `ISBN` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Anzahl` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ausgeliehen`
--

LOCK TABLES `ausgeliehen` WRITE;
/*!40000 ALTER TABLE `ausgeliehen` DISABLE KEYS */;
/*!40000 ALTER TABLE `ausgeliehen` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `buchstufe`
--

DROP TABLE IF EXISTS `buchstufe`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `buchstufe` (
  `stufe` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ISBN` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`stufe`,`ISBN`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `buchstufe`
--

LOCK TABLES `buchstufe` WRITE;
/*!40000 ALTER TABLE `buchstufe` DISABLE KEYS */;
/*!40000 ALTER TABLE `buchstufe` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `buecher`
--

DROP TABLE IF EXISTS `buecher`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `buecher` (
  `ISBN` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `Titel` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Verlag` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `preis` double(10,2) DEFAULT '0.00',
  PRIMARY KEY (`ISBN`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `buecher`
--

LOCK TABLES `buecher` WRITE;
/*!40000 ALTER TABLE `buecher` DISABLE KEYS */;
/*!40000 ALTER TABLE `buecher` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `protocolaus`
--

DROP TABLE IF EXISTS `protocolaus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `protocolaus` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `type` int DEFAULT NULL,
  `schuelerID` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `ISBN` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Anzahl` int DEFAULT NULL,
  `unix` int DEFAULT NULL,
  `user` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=48 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `protocolaus`
--

LOCK TABLES `protocolaus` WRITE;
/*!40000 ALTER TABLE `protocolaus` DISABLE KEYS */;
/*!40000 ALTER TABLE `protocolaus` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `protocollogin`
--

DROP TABLE IF EXISTS `protocollogin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `protocollogin` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `user` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `unix` int DEFAULT NULL,
  `erfolgreich` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `protocollogin`
--

LOCK TABLES `protocollogin` WRITE;
/*!40000 ALTER TABLE `protocollogin` DISABLE KEYS */;
/*!40000 ALTER TABLE `protocollogin` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `schueler`
--

DROP TABLE IF EXISTS `schueler`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `schueler` (
  `ID` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `Stufe` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Klasse` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Vorname` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Nachname` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Religion` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Fremdsp1` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Fremdsp2` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Fremdsp3` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `schueler`
--

LOCK TABLES `schueler` WRITE;
/*!40000 ALTER TABLE `schueler` DISABLE KEYS */;
/*!40000 ALTER TABLE `schueler` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `username` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `hash` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `privileges` int DEFAULT NULL,
  PRIMARY KEY (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2022-06-20 20:27:28
