# mtv_dl_web
A light-weight web UI for [mtv_dl](https://github.com/fnep/mtv_dl). It runs on your home lab and downloads the shows to your NAS.

## Deployment

This must be run behind some reverse proxy. Don't put it blindly in the public internet!


## TODOs

- For the MVP:
    - [ ] Create nice web ui for searching
    - [ ] Show database age on web ui, add a "update" button
    * [ ] Add a per-show download button
    * [ ] implement threading model and mutexes to avoid collisions
    * [ ] implement download queue
    * [ ] implement cron updates of the database
    * [ ] ... something about testing :)
    * [ ] containerize it, including all paths/mount points
    * [ ] forward backend errors to the frontend
* Cron searches
    * [ ] allow user to store filter queries
    * [ ] when updating the database, run those filter queries
    * [ ] notify the user about new downloads