import os


def check_output_file(file: str) -> str:
    allowed_dir = os.path.dirname(__file__)
    output_path = os.path.realpath(os.path.join(allowed_dir, file))
    if os.path.dirname(output_path) != allowed_dir:
        print("Error: OUTPUT_FILE must be in the script directory")
        exit(1)
    return output_path


allowed_dir = os.path.dirname(__file__)
output_path = os.path.realpath(os.path.join(allowed_dir, '../file'))
print(allowed_dir)
print(output_path)
# print(check_output_file("../config"))
