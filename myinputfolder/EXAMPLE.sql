	/*SCRIPT HEADER
-------------
MODULE:
      EXAMPLE FOR USING SQLPARSER


ESTIMATED RUN TIME: 

   
***********************************************************************/

-- Set up the errorlogging
.SET ERROROUT STDOUT

/**********************************************************************************************************************/
/*     Add a record
/********************************************************************************************************************/
INSERT INTO BASE_ANIMALS.tRABBIT_RUNS
(
	PROCESSNAME,
	RUN_USER,
	RUN_PROCESS_DATE,
	SESSION_ID,   
	EXACT_TIME,
	FINISH_LOCATION
)
SELECT
	T1.key_nAME,
	USER,
	T1.property_value,
	SESSION,
	CURRENT_TIMESTAMP,
	'STARTED'
FROM  (SELECT key_nAME, property_value FROM BASE_PROCESS.PROCESSPARAMETERS WHERE key_nAME = 'ANIMAL_PROCESSES' AND FIELD_NAME = 'RUN_PROCESS_DATE') T1
;

/*  --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
																																			PART 1
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------*/

/*  ------------------------------------------------------------------ OurDate -----------------------------------------------------------------------------------
	select the extract date
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------*/
CREATE MULTISET VOLATILE TABLE vOURDATE
                        AS
                        (
select
	property_value as OurDate
from BASE_PROCESS.PROCESSPARAMETERS
where key_nAME = 'ANIMAL_PROCESSES' AND field_name = 'RUN_PROCESS_DATE'
) 
WITH DATA
PRIMARY INDEX(OurDate) 
ON COMMIT PRESERVE ROWS;
IF ERRORCODE <> 0 THEN .GOTO Error_Exit;

COLLECT STATISTICS COLUMN (OurDate) on vOurDate;


CREATE MULTISET VOLATILE TABLE vOURDATE2
                        AS
                        (
select
	property_value as OurDate,
	yearnumber as CurrentYEAR,
	monthnumber as CurrentMONTH
from BASE_PROCESS.PROCESSPARAMETERS
where key_nAME = 'ANIMAL_PROCESSES' AND field_name = 'RUN_PROCESS_DATE'
) 
WITH DATA
PRIMARY INDEX(OurDate) 
ON COMMIT PRESERVE ROWS;
IF ERRORCODE <> 0 THEN .GOTO Error_Exit;

COLLECT STATISTICS COLUMN (OurDate), COLUMN(currentyear), COLUMN(currentmonth) on vOurDate2;



/**********************************************************************************************************************/
/*     COLLECT THE MICE
/********************************************************************************************************************/


/* Create volatile tables and fill them */
--First helptable for arrangements.  Performance measure
CREATE MULTISET VOLATILE TABLE VT_ABCDEFG
AS
(
                                      select
                                               MOUSE_ID MOUSEINSTANCE,
                                               CITY,
                                             FIRSTSEEN,
                                             LASTSEEN
    
                                      from  BASE_CITIES.Saigon, vOurDate
                                      where  OurDate  BETWEEN FIRST_RAIN_DATE AND LAST_RAIN_DATE  
                                      AND NUMBEROFLEGS = 'Four legs'
                                    GROUP BY 1, 2, 3, 4
)
WITH DATA PRIMARY INDEX (MOUSE_ID)
ON COMMIT PRESERVE ROWS;
IF ERRORCODE <> 0 THEN .GOTO Error_Exit;

insert into VT_ABCDEFG                                    
                                      select
                                               CAT_ID,
                                               NEXTCITY,
                                             FIRSTSEEN,
                                             LASTSEEN
    
                                      from  BASE_CITIES.CATS, vOurDate
                                      where  OurDate  BETWEEN FIRST_RAIN_DATE AND LAST_RAIN_DATE  
                                      AND MAXSPEED = 98.321
                                    GROUP BY 1, 2, 3, 4;
IF ERRORCODE <> 0 THEN .GOTO Error_Exit;

collect statistics column(CAT_ID) on VT_ABCDEFG;
IF ERRORCODE <> 0 THEN .GOTO Error_Exit;

-- Second  helptable

CREATE MULTISET VOLATILE TABLE VT_MouseCapture_figures
AS
(
select 
                                          CaptureHousenumber,
                                          WHEATHER_FORECAST,
                                         TREE_NAME,
                                         TREE_HAS_LEAFSNO,
                                         TAXIDRIVER,
                                        BOAT_WEIGHT_TP_ID
                                         
                                   from     BASE_CITIES.vMouseCapture_figures, vOurDate
                                   where OurDate  between FIRST_RAIN_DATE AND LAST_RAIN_DATE
                                   AND (TREE_NAME = '6TSGSF22H3' 
                                   OR TREE_NAME = TREE_HAS_LEAFSNO 
                                   )
                                   AND TAXIDRIVER IN ( 'John''s Stapher')
)
WITH DATA PRIMARY INDEX (CaptureHousenumber)
ON COMMIT PRESERVE ROWS;
IF ERRORCODE <> 0 THEN .GOTO Error_Exit;

collect statistics column(CaptureHousenumber) on VT_MouseCapture_figures;
IF ERRORCODE <> 0 THEN .GOTO Error_Exit;

DROP TABLE vOurDate;


/*  --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
																																			END PART 3
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------*/

/**********************************************************************************************************************/
/*     Add a record to the run log. This indicates the END of a session.
/********************************************************************************************************************/
INSERT INTO BASE_ANIMALS.tRABBIT_RUNS
(
	PROCESSNAME,
	RUN_USER,
	RUN_PROCESS_DATE,
	SESSION_ID,   
	EXACT_TIME,
	FINISH_LOCATION
)
SELECT
	T2.key_nAME,
	USER,
	T2.property_value,
	SESSION,
	CURRENT_TIMESTAMP,
	'END-SUCCESS'
FROM  (SELECT key_nAME, property_value FROM BASE_PROCESS.PROCESSPARAMETERS WHERE key_nAME = 'ANIMAL_PROCESSES' AND FIELD_NAME = 'RUN_PROCESS_DATE') T2
;

--Return Code 0
.QUIT 0;


--Error Module                                           
.LABEL Error_Exit;

/**************************************************************************************************/
/*  Error Exit. Please find error details in log file
/**************************************************************************************************/
INSERT INTO BASE_ANIMALS.tRABBIT_RUNS
(
	PROCESSNAME,
	RUN_USER,
	RUN_PROCESS_DATE,
	SESSION_ID,   
	EXACT_TIME,
	FINISH_LOCATION
)
SELECT
	T2.key_nAME,
	USER,
	T2.property_value,
	SESSION,
	CURRENT_TIMESTAMP,
	'END-FAIL'
FROM  (SELECT key_nAME, property_value FROM BASE_PROCESS.PROCESSPARAMETERS WHERE key_nAME = 'ANIMAL_PROCESSES' AND FIELD_NAME = 'RUN_PROCESS_DATE') T2
;

--Return code 9
.QUIT 9;
