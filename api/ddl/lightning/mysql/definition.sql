CREATE TABLE IF NOT EXISTS `lightning`.`bolt` (
  `id` VARCHAR(255) COLLATE utf8mb4_bin NOT NULL,
  `version` BIGINT NOT NULL DEFAULT 1,
  `home` VARCHAR(255) NOT NULL,
  `entity_id` VARCHAR(255),
  `name` VARCHAR(255),
  `description` VARCHAR(255),
  `what` JSON NOT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `lightning`.`forecast` (
  `id` VARCHAR(255) COLLATE utf8mb4_bin NOT NULL,
  `version` BIGINT NOT NULL DEFAULT 1,
  `home` VARCHAR(255) NOT NULL,
  `entity_id` VARCHAR(255),
  `name` VARCHAR(255),
  `description` VARCHAR(255),
  `what` JSON NOT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `lightning`.`forecast_scat` (
  `id` VARCHAR(255) COLLATE utf8mb4_bin NOT NULL,
  `forecast_id` VARCHAR(255),
  `scat_id` VARCHAR(255),
  `version` BIGINT NOT NULL DEFAULT 1,
  `home` VARCHAR(255) NOT NULL,
  `what` JSON NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE `forecast_id_scat_id` (`forecast_id`,`scat_id`)
);

CREATE TABLE IF NOT EXISTS `lightning`.`rod` (
  `id` VARCHAR(255) COLLATE utf8mb4_bin NOT NULL,
  `version` BIGINT NOT NULL DEFAULT 1,
  `home` VARCHAR(255) NOT NULL,
  `entity_id` VARCHAR(255),
  `name` VARCHAR(255),
  `selection` JSON NOT NULL,
  `act` JSON NOT NULL,
  `input` JSON NOT NULL,
  `what` JSON NOT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `lightning`.`strike` (
  `id` VARCHAR(255) COLLATE utf8mb4_bin NOT NULL,
  `version` BIGINT NOT NULL DEFAULT 1,
  `home` VARCHAR(255) NOT NULL,
  `entity_id` VARCHAR(255),
  `description` VARCHAR(255),
  `state` VARCHAR(255) NOT NULL DEFAULT 'created',
  `what` JSON NOT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `lightning`.`strike_scat` (
  `id` VARCHAR(255) COLLATE utf8mb4_bin NOT NULL,
  `strike_id` VARCHAR(255),
  `scat_id` VARCHAR(255),
  `version` BIGINT NOT NULL DEFAULT 1,
  `home` VARCHAR(255) NOT NULL,
  `what` JSON NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE `strike_id_scat_id` (`strike_id`,`scat_id`)
);
