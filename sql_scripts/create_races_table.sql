DROP TABLE IF EXISTS races;				
CREATE TABLE races
(
		date			date NOT NULL,
		country 		VARCHAR(10) NOT NULL,
		course			VARCHAR(25) NOT NULL,
		time			time NOT NULL DEFAULT '00:00:00',
		marketId		VARCHAR(25) NOT NULL,
		description		VARCHAR(25) NOT NULL,
        PRIMARY KEY (marketId)
);
