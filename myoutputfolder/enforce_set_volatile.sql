
CREATE /*BLA BLA*/ SET VOLATILE TABLE vOURDATE2
                        AS
                        (
SELECT
	property_value AS OurDate,
	yearnumber AS CurrentYEAR,
	monthnumber AS CurrentMONTH
FROM BASE_PROCESS.PROCESSPARAMETERS
WHERE key_nAME = 'ANIMAL_PROCESSES' AND field_name = 'RUN_PROCESS_DATE'
) 
WITH DATA
PRIMARY INDEX(OurDate) 
ON COMMIT PRESERVE ROWS;
IF ERRORCODE <> 0 THEN .GOTO Error_Exit;


CREATE MULTISET VOLATILE /*BLA BLA*/ TABLE vOURDATE2
                        AS
                        (
SELECT
	property_value AS OurDate,
	yearnumber AS CurrentYEAR,
	monthnumber AS CurrentMONTH
FROM BASE_PROCESS.PROCESSPARAMETERS
WHERE key_nAME = 'ANIMAL_PROCESSES' AND field_name = 'RUN_PROCESS_DATE'
) 
WITH DATA
PRIMARY INDEX(OurDate) 
ON COMMIT PRESERVE ROWS;
IF ERRORCODE <> 0 THEN .GOTO Error_Exit;


CREATE/*BLA BLA*/  VOLATILE TABLE vOURDATE2
                        AS
                        (
SELECT
	property_value AS OurDate,
	yearnumber AS CurrentYEAR,
	monthnumber AS CurrentMONTH
FROM BASE_PROCESS.PROCESSPARAMETERS
WHERE key_nAME = 'ANIMAL_PROCESSES' AND field_name = 'RUN_PROCESS_DATE'
) 
WITH DATA
PRIMARY INDEX(OurDate) 
ON COMMIT PRESERVE ROWS;
IF ERRORCODE <> 0 THEN .GOTO Error_Exit;










CREATE SET 
VOLATILE TABLE vOURDATE2
                        AS
                        (
SELECT
	property_value AS OurDate,
	yearnumber AS CurrentYEAR,
	monthnumber AS CurrentMONTH
FROM BASE_PROCESS.PROCESSPARAMETERS
WHERE key_nAME = 'ANIMAL_PROCESSES' AND field_name = 'RUN_PROCESS_DATE'
) 
WITH DATA
PRIMARY INDEX(OurDate) 
ON COMMIT PRESERVE ROWS;
IF ERRORCODE <> 0 THEN .GOTO Error_Exit;


CREATE
 MULTISET VOLATILE /*BLA BLA*/ TABLE vOURDATE2
                        AS
                        (
SELECT
	property_value AS OurDate,
	yearnumber AS CurrentYEAR,
	monthnumber AS CurrentMONTH
FROM BASE_PROCESS.PROCESSPARAMETERS
WHERE key_nAME = 'ANIMAL_PROCESSES' AND field_name = 'RUN_PROCESS_DATE'
) 
WITH DATA
PRIMARY INDEX(OurDate) 
ON COMMIT PRESERVE ROWS;
IF ERRORCODE <> 0 THEN .GOTO Error_Exit;


CREATE 
/*BLA BLA*/ 

VOLATILE TABLE vOURDATE2
                        AS
                        (
SELECT
	property_value AS OurDate,
	yearnumber AS CurrentYEAR,
	monthnumber AS CurrentMONTH
FROM BASE_PROCESS.PROCESSPARAMETERS
WHERE key_nAME = 'ANIMAL_PROCESSES' AND field_name = 'RUN_PROCESS_DATE'
) 
WITH DATA
PRIMARY INDEX(OurDate) 
ON COMMIT PRESERVE ROWS;
IF ERRORCODE <> 0 THEN .GOTO Error_Exit;


