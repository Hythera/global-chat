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
    `guild_id` BIGINT NOT NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`message_id`)
)