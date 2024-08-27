# widgets.py
from django.forms.widgets import ClearableFileInput

class CustomClearableFileInput(ClearableFileInput):
    allow_multiple_selected = True

    def format_value(self, value):
        """Return the file input value(s) as a list of files."""
        if self.is_initial(value):
            return [value]
        return value

    def value_from_datadict(self, data, files, name):
        """Return the file input value(s) from the data dictionary."""
        upload = files.getlist(name)
        if not upload:
            return []
        return upload
