from pathlib import Path

from mtv_dl_web import config


def test_load_config_reads_nested_database_refresh(tmp_path: Path) -> None:
    config_path = tmp_path / "mtv_dl_web.yaml"
    config_path.write_text(
        """
mtv_dl_database_dir: "./mtv_dl_db"
host: "127.0.0.1"
port: 8071
logging_level: "DEBUG"
download_basedir: "./Downloads/"
mtv_dl_targetdir: "{topic}/{start} {title}{ext}"
exclude_audiodeskription: true
database_refresh:
  enabled: true
  cron: "0 3 * * *"
  timezone: "Europe/Berlin"
""",
        encoding="utf-8",
    )

    loaded_config = config._load_config(config_path)

    assert loaded_config["database_refresh"] == {
        "enabled": True,
        "cron": "0 3 * * *",
        "timezone": "Europe/Berlin",
    }


def test_load_config_applies_environment_overrides(tmp_path: Path) -> None:
    config_path = tmp_path / "mtv_dl_web.yaml"
    config_path.write_text(
        """
mtv_dl_database_dir: "./mtv_dl_db"
host: "127.0.0.1"
port: 8071
logging_level: "DEBUG"
download_basedir: "./Downloads/"
mtv_dl_targetdir: "{topic}/{start} {title}{ext}"
exclude_audiodeskription: true
database_refresh:
  enabled: true
  cron: "0 3 * * *"
  timezone: "Europe/Berlin"
""",
        encoding="utf-8",
    )

    loaded_config = config._load_config(
        config_path,
        {
            "MTV_DL_WEB_MTV_DL_DATABASE_DIR": "/database",
            "MTV_DL_WEB_HOST": "0.0.0.0",
            "MTV_DL_WEB_PORT": "9090",
            "MTV_DL_WEB_LOGGING_LEVEL": "INFO",
            "MTV_DL_WEB_DOWNLOAD_BASEDIR": "/downloads",
            "MTV_DL_WEB_MTV_DL_TARGETDIR": "{channel}/{title}{ext}",
            "MTV_DL_WEB_EXCLUDE_AUDIODESKRIPTION": "false",
            "MTV_DL_WEB_DATABASE_REFRESH_ENABLED": "false",
            "MTV_DL_WEB_DATABASE_REFRESH_CRON": "30 4 * * *",
            "MTV_DL_WEB_DATABASE_REFRESH_TIMEZONE": "UTC",
        },
    )

    assert loaded_config["mtv_dl_database_dir"] == "/database"
    assert loaded_config["host"] == "0.0.0.0"
    assert loaded_config["port"] == 9090
    assert loaded_config["logging_level"] == "INFO"
    assert loaded_config["download_basedir"] == "/downloads"
    assert loaded_config["mtv_dl_targetdir"] == "{channel}/{title}{ext}"
    assert loaded_config["exclude_audiodeskription"] is False
    assert loaded_config["database_refresh"] == {
        "enabled": False,
        "cron": "30 4 * * *",
        "timezone": "UTC",
    }


def test_environment_overrides_can_create_database_refresh_config(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "mtv_dl_web.yaml"
    config_path.write_text(
        """
mtv_dl_database_dir: "./mtv_dl_db"
host: "127.0.0.1"
port: 8071
logging_level: "DEBUG"
download_basedir: "./Downloads/"
mtv_dl_targetdir: "{topic}/{start} {title}{ext}"
""",
        encoding="utf-8",
    )

    loaded_config = config._load_config(
        config_path,
        {
            "MTV_DL_WEB_DATABASE_REFRESH_ENABLED": "true",
            "MTV_DL_WEB_DATABASE_REFRESH_CRON": "0 5 * * *",
            "MTV_DL_WEB_DATABASE_REFRESH_TIMEZONE": "UTC",
        },
    )

    assert loaded_config["database_refresh"] == {
        "enabled": True,
        "cron": "0 5 * * *",
        "timezone": "UTC",
    }


def test_exclude_audiodeskription_defaults_to_true(tmp_path: Path) -> None:
    config_path = tmp_path / "mtv_dl_web.yaml"
    config_path.write_text(
        """
mtv_dl_database_dir: "./mtv_dl_db"
host: "127.0.0.1"
port: 8071
logging_level: "DEBUG"
download_basedir: "./Downloads/"
mtv_dl_targetdir: "{topic}/{start} {title}{ext}"
""",
        encoding="utf-8",
    )

    loaded_config = config._load_config(config_path, {})

    assert loaded_config.get("exclude_audiodeskription", True) is True
