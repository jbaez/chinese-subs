from app.subs_service import SubsService
from infra.file_info_reader import FileInfoReader


def main():
    file_path = ""
    file_reader = FileInfoReader()
    subs_service = SubsService(file_reader)
    subs_service.load_path(file_path)
    languages = subs_service.get_available_languages()
    print(languages)


if __name__ == '__main__':
    main()
