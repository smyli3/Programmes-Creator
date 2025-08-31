from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, IntegerField, FileField
from wtforms.validators import DataRequired, Optional, NumberRange
from flask_wtf.file import FileField, FileRequired, FileAllowed

class UploadForm(FlaskForm):
    """Form for uploading student data files."""
    file = FileField('Student Data File', validators=[
        FileRequired(),
        FileAllowed(['csv', 'xlsx', 'xls'], 'CSV or Excel files only!')
    ])
    program_id = StringField('Program ID', validators=[DataRequired()])
    submit = SubmitField('Upload')

class ProgramForm(FlaskForm):
    """Form for creating/editing programs."""
    name = StringField('Program Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    submit = SubmitField('Save')

class GroupForm(FlaskForm):
    """Form for creating/editing groups."""
    name = StringField('Group Name', validators=[DataRequired()])
    instructor = StringField('Instructor', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])
    max_size = IntegerField('Max Group Size', 
                          validators=[NumberRange(min=1, max=20)],
                          default=6)
    submit = SubmitField('Save')
