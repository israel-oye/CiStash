from typing import Any
from werkzeug.routing import BaseConverter


class CourseCodeConverter(BaseConverter):
    regex = r"^(?:[A-Z]{3}-[1-5][0-9]{2}|599|[1-9][0-9]*)$"

    def to_python(self, value: str) -> Any:
        if value.isdigit():
            return value
        course_code_segments = value.split("-")
        return " ".join(course_code_segments)

    def to_url(self, value: Any) -> str:
        if str(value).isdigit():
            return super().to_url(value)
        course_code_segments = value.split()
        return super().to_url("-".join(course_code_segments))
