SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

CREATE SCHEMA IF NOT EXISTS `ckanresources` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci ;
USE `ckanresources` ;

-- -----------------------------------------------------
-- Table `ckanresources`.`user`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ckanresources`.`user` (
  `user_id` VARCHAR(20) NOT NULL,
  `user_name` VARCHAR(120) NULL,
  `user_password` VARCHAR(120) NULL,
  `user_email` VARCHAR(120) NULL,
  `user_org` VARCHAR(120) NULL,
  PRIMARY KEY (`user_id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `ckanresources`.`authgroup`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ckanresources`.`authgroup` (
  `group_id` INT NOT NULL AUTO_INCREMENT,
  `group_name` VARCHAR(120) NOT NULL,
  PRIMARY KEY (`group_id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `ckanresources`.`usergroup`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ckanresources`.`usergroup` (
  `user_id` VARCHAR(20) NOT NULL,
  `group_id` INT NOT NULL,
  `join_date` DATETIME NOT NULL,
  PRIMARY KEY (`user_id`, `group_id`),
  INDEX `fk_usergroup_group1_idx` (`group_id` ASC),
  CONSTRAINT `fk_usergroup_user`
    FOREIGN KEY (`user_id`)
    REFERENCES `ckanresources`.`user` (`user_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_usergroup_group1`
    FOREIGN KEY (`group_id`)
    REFERENCES `ckanresources`.`authgroup` (`group_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `ckanresources`.`token`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ckanresources`.`token` (
  `token_id` VARCHAR(80) NOT NULL,
  `token_givendate` DATETIME NOT NULL,
  `token_givenby` VARCHAR(120) NOT NULL,
  PRIMARY KEY (`token_id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `ckanresources`.`tokenrequest`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ckanresources`.`tokenrequest` (
  `request_id` VARCHAR(80) NOT NULL,
  `request_date` DATETIME NOT NULL,
  `request_ip` VARCHAR(45) NOT NULL,
  `dataset_id` VARCHAR(80) NOT NULL,
  `resource_id` VARCHAR(80) NOT NULL,
  `user_name` VARCHAR(120) NULL,
  `user_email` VARCHAR(120) NULL,
  `user_org` VARCHAR(120) NULL,
  `user_orgtype` VARCHAR(45) NULL,
  `user_country` VARCHAR(45) NULL,
  `user_datausage` TEXT NULL,
  `user_otherdata` TEXT NULL,
  `user_hearfrom` VARCHAR(45) NULL,
  `token_given` VARCHAR(80) NULL,
  PRIMARY KEY (`request_id`),
  INDEX `fk_tokenrequest_token1_idx` (`token_given` ASC),
  CONSTRAINT `fk_tokenrequest_token1`
    FOREIGN KEY (`token_given`)
    REFERENCES `ckanresources`.`token` (`token_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `ckanresources`.`datasetoken`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ckanresources`.`datasetoken` (
  `dataset_id` VARCHAR(80) NOT NULL,
  `token_id` VARCHAR(80) NOT NULL,
  `grant_date` DATETIME NOT NULL,
  `grant_by` VARCHAR(120) NOT NULL,
  PRIMARY KEY (`dataset_id`, `token_id`),
  INDEX `fk_datasetoken_token1_idx` (`token_id` ASC),
  CONSTRAINT `fk_datasetoken_token1`
    FOREIGN KEY (`token_id`)
    REFERENCES `ckanresources`.`token` (`token_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `ckanresources`.`resourcetoken`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ckanresources`.`resourcetoken` (
  `resource_id` VARCHAR(80) NOT NULL,
  `token_id` VARCHAR(80) NOT NULL,
  `grant_date` DATETIME NULL,
  `grant_by` VARCHAR(10) NULL,
  PRIMARY KEY (`resource_id`, `token_id`),
  INDEX `fk_resourcetoken_token1_idx` (`token_id` ASC),
  CONSTRAINT `fk_resourcetoken_token1`
    FOREIGN KEY (`token_id`)
    REFERENCES `ckanresources`.`token` (`token_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `ckanresources`.`resourcestats`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ckanresources`.`resourcestats` (
  `request_id` VARCHAR(80) NOT NULL,
  `request_date` DATETIME NULL,
  `request_ip` VARCHAR(45) NULL,
  `resource_id` VARCHAR(80) NOT NULL,
  `resource_format` VARCHAR(45) NOT NULL,
  `token_id` VARCHAR(80) NULL,
  `user_id` VARCHAR(20) NULL,
  `request_name` VARCHAR(120) NULL,
  `request_email` VARCHAR(120) NULL,
  `request_org` VARCHAR(120) NULL,
  `request_orgtype` VARCHAR(45) NULL,
  `request_country` VARCHAR(45) NULL,
  `request_datausage` TEXT NULL,
  `request_hearfrom` VARCHAR(45) NULL,
  PRIMARY KEY (`request_id`),
  INDEX `fk_resourcestats_token1_idx` (`token_id` ASC),
  INDEX `fk_resourcestats_user1_idx` (`user_id` ASC),
  CONSTRAINT `fk_resourcestats_token1`
    FOREIGN KEY (`token_id`)
    REFERENCES `ckanresources`.`token` (`token_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_resourcestats_user1`
    FOREIGN KEY (`user_id`)
    REFERENCES `ckanresources`.`user` (`user_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `ckanresources`.`userdataset`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ckanresources`.`userdataset` (
  `dataset_id` VARCHAR(80) NOT NULL,
  `user_id` VARCHAR(20) NOT NULL,
  `grant_date` DATETIME NOT NULL,
  `grant_by` VARCHAR(120) NOT NULL,
  PRIMARY KEY (`dataset_id`, `user_id`),
  INDEX `fk_userdataset_user1_idx` (`user_id` ASC),
  CONSTRAINT `fk_userdataset_user1`
    FOREIGN KEY (`user_id`)
    REFERENCES `ckanresources`.`user` (`user_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `ckanresources`.`useresource`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ckanresources`.`useresource` (
  `resource_id` VARCHAR(80) NOT NULL,
  `user_id` VARCHAR(20) NOT NULL,
  `grant_date` DATETIME NOT NULL,
  `grant_by` VARCHAR(120) NOT NULL,
  PRIMARY KEY (`resource_id`, `user_id`),
  INDEX `fk_resourcedataset_user1_idx` (`user_id` ASC),
  CONSTRAINT `fk_resourcedataset_user1`
    FOREIGN KEY (`user_id`)
    REFERENCES `ckanresources`.`user` (`user_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `ckanresources`.`groupdataset`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ckanresources`.`groupdataset` (
  `dataset_id` VARCHAR(80) NOT NULL,
  `group_id` INT NOT NULL,
  `grant_date` DATETIME NOT NULL,
  `grant_by` VARCHAR(120) NOT NULL,
  PRIMARY KEY (`dataset_id`, `group_id`),
  INDEX `fk_groupdataset_group1_idx` (`group_id` ASC),
  CONSTRAINT `fk_groupdataset_group1`
    FOREIGN KEY (`group_id`)
    REFERENCES `ckanresources`.`authgroup` (`group_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `ckanresources`.`groupresource`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ckanresources`.`groupresource` (
  `resource_id` VARCHAR(80) NOT NULL,
  `group_id` INT NOT NULL,
  `grant_date` DATETIME NOT NULL,
  `grant_by` VARCHAR(120) NOT NULL,
  PRIMARY KEY (`resource_id`, `group_id`),
  INDEX `fk_groupresource_group1_idx` (`group_id` ASC),
  CONSTRAINT `fk_groupresource_group1`
    FOREIGN KEY (`group_id`)
    REFERENCES `ckanresources`.`authgroup` (`group_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
