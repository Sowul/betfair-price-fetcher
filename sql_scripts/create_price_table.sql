DROP TABLE IF EXISTS price;
CREATE TABLE price
(
        marketId	    VARCHAR(25) NOT NULL,
        runnerId        INT(11) NOT NULL,
        runner          VARCHAR(25) NOT NULL,
        date            date NOT NULL,
        timestamp       time NOT NULL,
        back            DECIMAL(6,2),
        backvol1        DECIMAL(9,2),
        total_back3     DECIMAL(9,2),
        lastprice       DECIMAL(6,2),
        wom             DECIMAL(3,2),
        lay             DECIMAL(6,2),
        layvol1         DECIMAL(9,2),
        total_lay3      DECIMAL(9,2),
        PRIMARY KEY (marketId, runnerId, timestamp)
);
