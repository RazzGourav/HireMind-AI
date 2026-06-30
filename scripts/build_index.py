from _bootstrap import ensure_project_environment

ensure_project_environment()

from hiremind.interfaces.cli.build_index import main  # noqa: E402

if __name__ == "__main__":
    main()
