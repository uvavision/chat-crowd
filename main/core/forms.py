from flask_wtf import FlaskForm
from wtforms.fields import (StringField, SubmitField, RadioField, SelectField,
                            SelectMultipleField, IntegerField, FloatField,
                            TextAreaField)
from wtforms.validators import Required
from wtforms import widgets
from .const import MODE_WOZ_CHAT, MODE_WOZ_QA
from .. import LST_META


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class LoginForm(FlaskForm):
    workerid = StringField('worderid', id='workerid', validators=[Required()], render_kw={"placeholder": "Enter you contributor ID..."})
    # username = StringField('username', id="username", validators=[Required()], default="user_default")
    task_id = StringField('task_id', id="task_id", validators=[Required()], default="57870")
    role = RadioField('role', choices=[('user', 'instructor'), ('agent', 'painter')],
                      validators=[Required()])
    mode = RadioField('mode', choices=[(MODE_WOZ_CHAT, MODE_WOZ_CHAT),
                      (MODE_WOZ_QA, MODE_WOZ_QA)], validators=[Required()])
    submit = SubmitField('Start', id='login')


class TestFormUser(FlaskForm):
    '''add test for user'''
    submit = SubmitField('Submit', id='test_submit')


class TestFormAgent(FlaskForm):
    '''add test for agent'''
    submit = SubmitField('Submit', id='test_submit')


class FeedbackForm(FlaskForm):
    feedback = TextAreaField('feedback', id='feedback',
                             validators=[Required()])
    submit = SubmitField('Submit', id='feedback_submit')
