
-- select name, type from mysql.proc where db = database() order by type, name;

-- DROP PROCEDURE <stored procedure name>; 



-- Creer la table des USER

CREATE TABLE `adneomblog`.`tbl_user` (
  `user_id` BIGINT NULL AUTO_INCREMENT,
  `user_email` VARCHAR(45) NULL,
  `user_password` VARCHAR(45) NULL,
  PRIMARY KEY (`user_id`));

-- procederure pour valider un user
DELIMITER $$
USE `adneomblog`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_validateLogin`(
IN p_email VARCHAR(45)
)
BEGIN
    select * from tbl_user where user_email = p_email;
END$$
DELIMITER ;




-- Creer la table des post

CREATE TABLE `tbl_post` (
  `post_id` int(11) NOT NULL AUTO_INCREMENT,
  `post_title` varchar(150) DEFAULT NULL,
  `post_subtitle` varchar(150) DEFAULT NULL,
  `post_author` varchar(45) DEFAULT NULL,
  `post_content` varchar(5000) DEFAULT NULL,
  `post_user_id` int(11) DEFAULT NULL,
  `post_date` datetime DEFAULT NULL,
  PRIMARY KEY (`post_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;


-- procedure pour ajouter un post

USE `adneomblog`;
DROP procedure IF EXISTS `adneomblog`.`sp_addpost`;
 
DELIMITER $$
USE `adneomblog`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_addpost`(
    IN p_title varchar(150),
	IN p_subtitle varchar(150),
	IN p_author varchar(45),
    IN p_content varchar(5000),
    IN p_user_id bigint
)
BEGIN
    insert into tbl_post(
        post_title,
		post_subtitle,
		post_author,
        post_content,
        post_user_id,
        post_date
    )
    values
    (
        p_title,
		p_subtitle,
		p_author,
        p_content,
        p_user_id,
        NOW()
    );
END$$
 
DELIMITER ;
;

-- procedure pour recuperer tous les post ajouter par admin

USE `adneomblog`;
DROP procedure IF EXISTS `sp_GetBlogByUser`;
 
DELIMITER $$
USE `adneomblog`$$
CREATE PROCEDURE `sp_GetBlogByUser` (
IN p_user_id bigint
)
BEGIN
    select * from tbl_post where post_user_id = p_user_id order by post_date DESC;
END$$
 
DELIMITER ;

-- entre deux
USE `adneomblog`;
DROP procedure IF EXISTS `sp_GetBlogByUser`;
 
DELIMITER $$
USE `adneomblog`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_GetBlogByUser`(
IN p_user_id bigint,
IN p_limit int,
IN p_offset int
)
BEGIN
    SET @t1 = CONCAT( 'select * from tbl_post where post_user_id = ', p_user_id, ' order by post_date desc limit ',p_limit,' offset ',p_offset);
    PREPARE stmt FROM @t1;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt1;
END$$
 
DELIMITER ;

-- Nouvelle procedure pour recuperer la liste des post avec pagination
USE `adneomblog`;
DROP procedure IF EXISTS `sp_GetBlogByUser`;
 
DELIMITER $$
USE `adneomblog`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_GetBlogByUser`(
IN p_user_id bigint,
IN p_limit int,
IN p_offset int,
out p_total bigint
)
BEGIN
     
    select count(*) into p_total from tbl_post where post_user_id = p_user_id;
 
    SET @t1 = CONCAT( 'select * from tbl_post where post_user_id = ', p_user_id, ' order by post_date desc limit ',p_limit,' offset ',p_offset);
    PREPARE stmt FROM @t1;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END$$
 
DELIMITER ;

-- procedure pour recuperer un blog post par Id et user admin
USE `adneomblog`;
DROP procedure IF EXISTS `sp_GetBlogPostById`;

DELIMITER $$
USE `adneomblog`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_GetBlogPostById`(
IN p_blog_id bigint,
In p_user_id bigint
)
BEGIN
select * from tbl_post where post_id = p_blog_id and post_user_id = p_user_id ;
END$$
 
DELIMITER ;

-- procedure pour modifier mon contenue

DELIMITER $$
USE `adneomblog`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_updateBlogPost`(
IN p_title varchar(150),
IN p_subtitle varchar(150),
IN p_author varchar(45),
IN p_content varchar(5000),
IN p_blog_id bigint,
In p_user_id bigint
)
BEGIN
update tbl_post set post_title = p_title,post_subtitle = p_subtitle,post_author = p_author,post_content = p_content
    where post_id = p_blog_id and post_user_id = p_user_id;
END$$
DELIMITER ;

-- procdedure pour supprimer un  post
DELIMITER $$
USE `adneomblog`$$
CREATE PROCEDURE `sp_deleteBlogPost` (
IN p_blog_id bigint,
IN p_user_id bigint
)
BEGIN
delete from tbl_post where post_id = p_blog_id and post_user_id = p_user_id;
END$$
 
DELIMITER ;

-- get all post

-- procedure pour recuperer tous les post ajouter par admin

USE `adneomblog`;
DROP procedure IF EXISTS `sp_GetAllPost`;
 
DELIMITER $$
USE `adneomblog`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_GetAllPost`()
BEGIN
    select post_id,post_title,post_subtitle,post_author,post_date from tbl_post order by post_date DESC;
END$$
 
DELIMITER ;

-- procedure pour afficher les infos sur du post selectionner

USE `adneomblog`;
DROP procedure IF EXISTS `sp_GetPostById`;
 
DELIMITER $$
USE `adneomblog`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_GetPostById`(
IN p_blog_id bigint
)
BEGIN
    select * from tbl_post where post_id = p_blog_id;
END$$
 
DELIMITER ;