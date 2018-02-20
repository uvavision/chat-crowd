from flask_wtf import FlaskForm
from wtforms.fields import (StringField, SubmitField, RadioField, SelectField,
                            SelectMultipleField, IntegerField, FloatField,
                            TextAreaField)
from wtforms.validators import Required
from wtforms import widgets
from .const import NAME, MODE_WOZ_HUMAN, MODE_WOZ_MTS, MODE_BOT
from .metadata_processor import metadata2form
from .. import LST_META


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class LoginForm(FlaskForm):
    workerid = StringField('worderid', id='workerid', validators=[Required()], default="test123")
    username = StringField('username', id="username", validators=[Required()])
    task_id = StringField('task_id', id="task_id", validators=[Required()], default="57870")
    role = RadioField('role', choices=[('user', 'instructor'), ('agent', 'painter')],
                      validators=[Required()])
    mode = RadioField('mode', choices=[('chat', 'chat'), ('qa', 'qa')], validators=[Required()])
    submit = SubmitField('Start', id='login')


class LookupForm(FlaskForm):
    d_func = {'IntegerField': IntegerField, 'StringField': StringField,
              'FloatField': FloatField, 'SelectField': SelectField,
              'SelectMultipleField': SelectMultipleField}
    for d_meta in LST_META:
        for func, d in metadata2form(list(d_meta.items())[0][-1]):
            if func in ['SelectField', 'SelectMultipleField']:
                tmp = d_func[func](d[NAME], choices=d['choices'], id=d[NAME])
            else:
                tmp = d_func[func](d[NAME], id=d[NAME])
            exec(d[NAME] + ' = tmp')
    submit = SubmitField('Search', id='search')


class TestFormUser(FlaskForm):
    lst_rental = []
    for i, ele in enumerate(['None of below', 'rent/price', '#bedroom',
                             'transportation', 'neighborhood/location']):
        lst_rental.append((i, ele))
    rental = MultiCheckboxField('rental info', id='rental', choices=lst_rental)
    lst_nei = []
    for ele in ['Downtown Brooklyn', 'Tribeca', 'Yorktown Heights', 'Midtown']:
        lst_nei.append((ele, ele))
    neighborhood = MultiCheckboxField('neighborhood', choices=lst_nei)
    submit = SubmitField('Submit', id='test_submit')


class TestFormAgent(FlaskForm):
    r1 = IntegerField('Search Results Total', id='r1', validators=[Required()])
    r2 = IntegerField('Search Results Total', id='r2', validators=[Required()])
    r3 = IntegerField('Search Results Total', id='r3', validators=[Required()])
    submit = SubmitField('Submit', id='test_submit')


class FeedbackForm(FlaskForm):
    feedback = TextAreaField('feedback', id='feedback',
                             validators=[Required()])
    submit = SubmitField('Submit', id='feedback_submit')
