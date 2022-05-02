# map

Purpose : Produce quality reports

Steps :
1) Initiate the data in a sqlite DB

    1a) Automated -  Prepare files to import
        - Create two folders : Pimkie, Jules
        - Create empty files
        - Ask to populate the files and confirm when done
    1b) Manual - Get the data
        - export these tables in CSV (using default parameters)
            - adm_user
            - adm_profile_user
            - request_history
        - Fill the empty files
    1c) Automated - Populate the DB
        - truncate adm_user, adm_profile_user, request_history
        - load the tables from the files
2) Automated : Generate the Indicators
