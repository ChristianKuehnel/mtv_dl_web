# mtv_dl_web
A light-weight web UI for [mtv_dl](https://github.com/fnep/mtv_dl). It runs on your home lab and downloads the shows to your NAS.

## Deployment

This must be run behind some reverse proxy. Don't put it blindly in the public internet!

### Run With Docker Or Podman

The service listens on port `8071` inside the container and expects three mounted directories:

- `/config`: contains `mtv_dl_web.yaml`
- `/downloads`: where downloaded shows are written
- `/database`: where the `mtv_dl` database is stored

Container images are published to the GitHub Container Registry:

<https://github.com/ChristianKuehnel/mtv_dl_web/pkgs/container/mtv_dl_web>

Pull the image with Podman:

```sh
podman pull ghcr.io/christiankuehnel/mtv_dl_web:latest
```

Or with Docker:

```sh
docker pull ghcr.io/christiankuehnel/mtv_dl_web:latest
```

The easiest way to run the container from this checkout is:

To run it with Podman:

```sh
podman run --rm \
  --name mtv-dl-web \
  -p 8071:8071 \
  -v "$PWD/config:/config" \
  -v "$PWD/Downloads:/downloads" \
  -v "$PWD/mtv_dl_db:/database" \
  ghcr.io/christiankuehnel/mtv_dl_web:latest
```

With Docker Compose use this snippet:

```yaml
services:
  mtv-dl-web:
    image: ghcr.io/christiankuehnel/mtv_dl_web:latest
    container_name: mtv-dl-web
    restart: unless-stopped
    ports:
      - "8071:8071"
    volumes:
      - ./config:/config
      - ./Downloads:/downloads
      - ./mtv_dl_db:/database
    environment:
      MTV_DL_WEB_LOGGING_LEVEL: "INFO"
      MTV_DL_WEB_DATABASE_REFRESH_CRON: "0 3 * * *"
```

### Configuration

The container reads `/config/mtv_dl_web.yaml`. A container-ready example lives
at `config/mtv_dl_web.yaml`:

```yaml
mtv_dl_database_dir: "/database"
host: "0.0.0.0"
port: 8071
logging_level: "INFO"
download_basedir: "/downloads"
mtv_dl_targetdir: "{topic}/{start} {title}{ext}"
database_refresh:
  enabled: true
  cron: "0 3 * * *"
  timezone: "Europe/Berlin"
```

Configuration parameters:

- `mtv_dl_database_dir`: directory used by `mtv_dl` for its database. In the
  container this should normally be `/database`.
- `host`: address the web server binds to. Use `0.0.0.0` inside the container.
- `port`: port the web server listens on inside the container. The image exposes
  `8071`.
- `logging_level`: Python logging level, for example `INFO` or `DEBUG`.
- `download_basedir`: user-facing download base directory. In the container this
  should normally be `/downloads`.
- `mtv_dl_targetdir`: `mtv_dl` target template below `download_basedir`.
- `database_refresh.enabled`: whether scheduled database refreshes are enabled.
- `database_refresh.cron`: five-field cron expression for scheduled refreshes.
  Quote this value because `*` has YAML meaning.
- `database_refresh.timezone`: timezone used to interpret the cron expression,
  for example `Europe/Berlin`.

The default cron expression `0 3 * * *` refreshes the database every day at
03:00 in the configured timezone. Manual refreshes from the web UI and scheduled
refreshes use the same work queue as downloads, so downloads and refreshes run
one at a time.

All configuration parameters can also be set through environment variables.
Environment variables take precedence over `mtv_dl_web.yaml`. Use the
`MTV_DL_WEB_` prefix to avoid name collisions:

- `MTV_DL_WEB_CONFIG`: path to the config file. Defaults to
  `/config/mtv_dl_web.yaml` in the container.
- `MTV_DL_WEB_MTV_DL_DATABASE_DIR`: overrides `mtv_dl_database_dir`.
- `MTV_DL_WEB_HOST`: overrides `host`.
- `MTV_DL_WEB_PORT`: overrides `port`.
- `MTV_DL_WEB_LOGGING_LEVEL`: overrides `logging_level`.
- `MTV_DL_WEB_DOWNLOAD_BASEDIR`: overrides `download_basedir`.
- `MTV_DL_WEB_MTV_DL_TARGETDIR`: overrides `mtv_dl_targetdir`.
- `MTV_DL_WEB_DATABASE_REFRESH_ENABLED`: overrides
  `database_refresh.enabled`. Accepted boolean values are `true`, `false`, `1`,
  `0`, `yes`, `no`, `on`, and `off`.
- `MTV_DL_WEB_DATABASE_REFRESH_CRON`: overrides `database_refresh.cron`.
- `MTV_DL_WEB_DATABASE_REFRESH_TIMEZONE`: overrides
  `database_refresh.timezone`.

For example, to disable scheduled refreshes while keeping the rest of the YAML
file:

```sh
podman run --rm \
  --name mtv-dl-web \
  -p 8071:8071 \
  -v "$PWD/config:/config" \
  -v "$PWD/Downloads:/downloads" \
  -v "$PWD/mtv_dl_db:/database" \
  -e MTV_DL_WEB_DATABASE_REFRESH_ENABLED=false \
  ghcr.io/christiankuehnel/mtv_dl_web:latest
```


## TODOs

List of things I want to implement:

- For the MVP:
    - [x] Create nice web ui for searching
    - [x] Show database age on web ui, add a "update" button
    * [x] Add a per-show download button
    * [x] Add config parameter for the download folder
    * [x] containerize it, including all paths/mount points
    * [x] implement threading model and mutexes to avoid collisions
    * [x] implement download queue
    * [x] implement cron updates of the database
    * [ ] ... something about testing :)
    * [x] forward backend errors to the frontend
    * [x] in the container: use environment variables over the config file
    * [x] fix WARNING: "This is a development server. Do not use it in a production deployment. Use a production WSGI server instead."
    * [x] update the queue so that it shows the title of the show, not just the hash, probably do that in the backend when enquing something
    * [ ] duration parameter doesn't work
    * [ ] cover different combinations of search queries
    * [ ] create a `mtv_dl` mock for testing, to not depend on live data
* Cron searches
    * [ ] allow user to store filter queries
    * [ ] when updating the database, run those filter queries
* maybe some day
    * [ ] support a different output path when downloading series
    * [ ] support a post-download script and/or notify the user about new downloads
