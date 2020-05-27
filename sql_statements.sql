CREATE SCHEMA IF NOT EXISTS `amazon` DEFAULT CHARACTER SET utf8;

USE `amazon`;

 create table if not exists reviews
(
    customer_id varchar(20),
    product_id varchar(10),
    marketplace char(2),
    review_body text not null,
    helpful_votes int not null,
    total_votes int not null,
    review_date datetime not null,
    review_headline varchar(10000) not null,
    product_category varchar(100),
    verified_purchase boolean,
    star_rating int,
    primary key (customer_id, product_id)
);