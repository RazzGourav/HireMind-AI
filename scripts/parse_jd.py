from _bootstrap import ensure_project_environment

ensure_project_environment()

from hiremind.interfaces.cli.jd_cli import main  # noqa: E402

if __name__ == "__main__":
    main()
