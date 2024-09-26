CREATE TABLE IF NOT EXISTS `global_channels` (
    `channel_id` BIGINT NOT NULL,
    `guild_id` BIGINT NOT NULL,
    `invite` VARCHAR(255) NOT NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`channel_id`)
)