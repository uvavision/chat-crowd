from flask_wtf import FlaskForm
from wtforms.fields import (StringField, SubmitField, RadioField, SelectField,
                            SelectMultipleField, IntegerField, FloatField,
                            TextAreaField)
from wtforms.validators import Required
from wtforms import widgets
from .data import load_quiz_data
from .const import MODE_2D, MODE_COCO, AGENT, USER, Q, C, A, DATA

data_test = load_quiz_data()


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class LoginForm(FlaskForm):
    workerid = StringField('worderid', id='workerid', validators=[Required()])
    username = StringField('username', id="username", validators=[Required()])
    # workerid = StringField('worderid', id='workerid', validators=[Required()], render_kw={"placeholder": "Enter your contributor ID..."})
    # username = StringField('username', id="username", validators=[Required()], render_kw={"placeholder": "Enter your CrowdFlower UserName..."})
    task_id = StringField('task_id', id="task_id", validators=[Required()], default="12445")
    tasks = StringField('tasks', id="tasks", validators=None, default="12445")
    role = RadioField('role', choices=[('user', 'instructor'), ('agent', 'painter')],
                      validators=[Required()])
    mode = RadioField('mode', choices=[('2Dshape', "2D shapes"),
                      ("COCO", "Real Images")], validators=[Required()])
    submit = SubmitField('Start', id='login')


class TestForm2DAgent(FlaskForm):
    '''add test for user'''
    data = data_test[MODE_2D][AGENT]
    r1 = MultiCheckboxField(data[0][Q], choices=data[0][C], description=data[0][Q], validators=[Required()])
    r1data = data[0][DATA]
    r2 = MultiCheckboxField(data[1][Q], choices=data[1][C], description=data[1][Q], validators=[Required()])
    answers = [data[0][A], data[1][A]]
    submit = SubmitField('Submit', id='test_submit')


class TestForm2DUser(FlaskForm):
    '''add test for user'''
    data = data_test[MODE_2D][USER]
    r1 = MultiCheckboxField(data[0][Q], choices=data[0][C], description=data[0][Q], validators=[Required()])
    r1data = data[0][DATA]
    r2 = MultiCheckboxField(data[1][Q], choices=data[1][C], description=data[1][Q], validators=[Required()])
    answers = [data[0][A], data[1][A]]
    submit = SubmitField('Submit', id='test_submit')


class TestFormCOCOAgent(FlaskForm):
    '''add test for user'''
    data = data_test[MODE_COCO][AGENT]
    r1 = MultiCheckboxField(data[0][Q], choices=data[0][C], description=data[0][Q], validators=[Required()])
    r1data = data[0][DATA]
    r2 = MultiCheckboxField(data[1][Q], choices=data[1][C], description=data[1][Q], validators=[Required()])
    answers = [data[0][A], data[1][A]]
    submit = SubmitField('Submit', id='test_submit')


class TestFormCOCOUser(FlaskForm):
    '''add test for user'''
    data = data_test[MODE_COCO][USER]
    r1 = MultiCheckboxField(data[0][Q], choices=data[0][C], description=data[0][Q], validators=[Required()])
    r1data = data[0][DATA]
    r2 = MultiCheckboxField(data[1][Q], choices=data[1][C], description=data[1][Q], validators=[Required()])
    answers = [data[0][A], data[1][A]]
    submit = SubmitField('Submit', id='test_submit')


class FeedbackForm(FlaskForm):
    feedback = TextAreaField('feedback', id='feedback',
                             validators=[Required()])
    submit = SubmitField('Submit', id='feedback_submit')


class DialogActForm(FlaskForm):
    INFORM = 'inform'
    CONFIRM = 'confirm'
    REJECT = 'reject'
    REQUEST = 'request'  # instruct
    SELF_CORRECTION = 'self-correction'
    ASK_Q = 'ask-question'
    END = 'end-conversation'
    DAS = [INFORM, CONFIRM, REQUEST, REJECT, SELF_CORRECTION]
    choices = [(ele, ele.upper()) for ele in DAS]
    choices = [("", 'Choose Dialog Act')] + choices
    da = SelectField('da', choices=choices, id='da')
