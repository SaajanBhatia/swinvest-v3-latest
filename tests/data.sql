CREATE TABLE 'accounts' (
    'UID' INT NOT NULL PRIMARY KEY,
    'username' VARCHAR(100),
    'firstName' VARCHAR(100),
    'lastName' VARCHAR(100),
    'password' VARCHAR(500)
);

CREATE TABLE `preferences` (
  `pid` INT NOT NULL,
  `one` VARCHAR(50) DEFAULT NULL,
  `two` VARCHAR(50) DEFAULT NULL,
  `three` VARCHAR(50) DEFAULT NULL,
  `four` VARCHAR(50) DEFAULT NULL,
  `five` VARCHAR(50) DEFAULT NULL,
  PRIMARY KEY (`pid`)
);