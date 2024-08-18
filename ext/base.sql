CREATE TABLE `users` (
    `id` INT(11) UNSIGNED PRIMARY KEY AUTO_INCREMENT NOT NULL,
    `uid` BIGINT(19) UNSIGNED NOT NULL,
    `messages` INT(11) UNSIGNED DEFAULT 0,
    `voice_activity` INT(11) UNSIGNED DEFAULT 0
);

CREATE TABLE `voice_activity_history` (
    `id` INT(11) UNSIGNED PRIMARY KEY AUTO_INCREMENT NOT NULL,
    `uid` BIGINT(19) UNSIGNED NOT NULL,
    `join_on` INT(11) UNSIGNED,
    `left_on` INT(11) UNSIGNED,
    `total` INT(11) UNSIGNED
);

CREATE TABLE `soundboard` (
    `id` INT(11) UNSIGNED PRIMARY KEY AUTO_INCREMENT NOT NULL,
    `author` BIGINT(19) UNSIGNED NOT NULL,
    `name` VARCHAR(32) NOT NULL,
    `file_extension` VARCHAR(8) NOT NULL,
    `sha256` VARCHAR(64) NOT NULL
)
