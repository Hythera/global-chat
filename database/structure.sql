CREATE TABLE IF NOT EXISTS `global_channels` (
    `channel_id` BIGINT NOT NULL,
    `guild_id` BIGINT NOT NULL,
    `invite` VARCHAR(255) NOT NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`channel_id`)
);
CREATE TABLE IF NOT EXISTS `message_ids` (
    `uuid` VARCHAR(255) NOT NULL,
    `message_id` BIGINT NOT NULL,
    `channel_id` BIGINT NOT NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`message_id`)
);
CREATE TABLE IF NOT EXISTS `message_infos` (
    `uuid` VARCHAR(255) NOT NULL,
    `original_message_id` BIGINT NOT NULL,
    `original_channel_id` BIGINT NOT NULL,
    `author_id` BIGINT NOT NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`uuid`)
);
CREATE TABLE IF NOT EXISTS `user_roles` (
    `user_id` BIGINT NOT NULL,
    `role` VARCHAR(255) NOT NULL,
    `display_role` VARCHAR(255) Not NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`user_id`)
);
CREATE TABLE IF NOT EXISTS `mutes` (
    `user_id` BIGINT NOT NULL,
    `staff_id` BIGINT NOT NULL,
    `reason` VARCHAR(1024) NOT NULL,
    `expires_at` TIMESTAMP NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`user_id`)
)