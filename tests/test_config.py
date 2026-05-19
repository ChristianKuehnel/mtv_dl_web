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
