-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Tempo de geração: 20/11/2026 às 02:01
-- Versão do servidor: 10.4.32-MariaDB
-- Versão do PHP: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Banco de dados: `db_robo`
--
CREATE DATABASE IF NOT EXISTS `db_robo` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `db_robo`;

-- --------------------------------------------------------

--
-- Estrutura para tabela `viagens`
--

DROP TABLE IF EXISTS `viagens`;
CREATE TABLE `viagens` (
  `id` int(11) NOT NULL,
  `data_hora` datetime NOT NULL,
  `distancia_cm` decimal(6,2) NOT NULL,
  `velocidade` int(11) DEFAULT 0,
  `acao` varchar(50) DEFAULT 'andar_cm',
  `valor` float DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Despejando dados para a tabela `viagens`
--

INSERT INTO `viagens` (`id`, `data_hora`, `distancia_cm`, `velocidade`, `acao`, `valor`) VALUES
(1, '2020-04-11 18:57:30', 10.16, 0, 'andar_cm', 0),
(2, '2020-04-11 18:57:49', 10.23, 0, 'andar_cm', 0),
(3, '2020-04-11 18:59:03', 10.43, 0, 'andar_cm', 0),
(4, '2020-04-11 19:00:42', 70.10, 0, 'andar_cm', 0),
(5, '2020-04-11 19:01:11', 70.19, 0, 'andar_cm', 0),
(6, '2026-11-19 21:36:20', 10.18, 20, 'andar_cm', 0),
(7, '2026-11-19 21:45:56', 10.18, 20, 'andar_cm', 0),
(8, '2026-11-19 21:46:03', 10.00, 20, 'andar_cm', 0),
(9, '2026-11-19 21:47:00', 10.00, 20, 'andar_cm', 0),
(10, '2026-11-19 21:47:26', 10.00, 20, 'andar_cm', 0),
(11, '2026-11-19 21:47:47', 120.00, 20, 'andar_cm', 0),
(12, '2026-11-19 21:52:39', 10.21, 20, 'andar_cm', 10),
(13, '2026-11-19 21:52:56', 120.00, 20, 'cacamba', 120),
(14, '2026-11-19 21:53:07', 120.00, 20, 'cacamba', 120),
(15, '2026-11-19 21:54:21', 120.00, 20, 'cacamba', 120),
(16, '2026-11-19 21:56:13', 1.00, 20, 'girar_seg', 1),
(17, '2026-11-19 21:56:38', 10.18, 20, 'andar_cm', 10),
(18, '2026-11-19 21:56:45', 10.21, 20, 'andar_cm', 10),
(19, '2026-11-19 21:57:01', 120.00, 20, 'cacamba', 120),
(20, '2026-11-19 21:57:34', 1.00, 20, 'girar_seg', 1);

--
-- Índices para tabelas despejadas
--

--
-- Índices de tabela `viagens`
--
ALTER TABLE `viagens`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT para tabelas despejadas
--

--
-- AUTO_INCREMENT de tabela `viagens`
--
ALTER TABLE `viagens`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
